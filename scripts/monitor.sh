#!/bin/bash

###############################################################################
# OHMVISION - MONITORING AUTOMATIQUE
# Script de surveillance des services et auto-restart
###############################################################################

set -e

# Configuration
LOG_FILE="/var/log/ohmvision-monitor.log"
WEBHOOK_URL="${WEBHOOK_URL:-}"  # URL pour notifications (Discord, Slack, etc.)

# Fonction de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Fonction de notification
notify() {
    local message="$1"
    log "$message"
    
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"🚨 OhmVision Alert: $message\"}" \
            &> /dev/null || true
    fi
}

# Vérifier si Docker tourne
check_docker() {
    if ! systemctl is-active --quiet docker; then
        notify "CRITICAL: Docker service is down! Restarting..."
        systemctl restart docker
        sleep 5
    fi
}

# Vérifier les services
check_services() {
    cd /opt/ohmvision
    
    # Liste des services critiques
    SERVICES=("postgres" "redis" "backend" "frontend" "nginx")
    
    for service in "${SERVICES[@]}"; do
        # Vérifier si le container tourne
        if ! docker-compose -f docker-compose.production.yml ps | grep -q "$service.*Up"; then
            notify "WARNING: Service $service is down! Restarting..."
            docker-compose -f docker-compose.production.yml restart "$service"
            sleep 10
        fi
        
        # Vérifier le health check
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "ohmvision_$service" 2>/dev/null || echo "no-health")
        
        if [ "$HEALTH" == "unhealthy" ]; then
            notify "WARNING: Service $service is unhealthy! Restarting..."
            docker-compose -f docker-compose.production.yml restart "$service"
            sleep 10
        fi
    done
}

# Vérifier l'espace disque
check_disk_space() {
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$DISK_USAGE" -gt 90 ]; then
        notify "CRITICAL: Disk usage is at ${DISK_USAGE}%! Cleaning up..."
        
        # Nettoyer les logs anciens
        find /opt/ohmvision/logs -name "*.log" -mtime +7 -delete
        
        # Nettoyer Docker
        docker system prune -f --volumes
        
        log "Cleanup completed"
    elif [ "$DISK_USAGE" -gt 80 ]; then
        notify "WARNING: Disk usage is at ${DISK_USAGE}%"
    fi
}

# Vérifier la mémoire
check_memory() {
    MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    
    if [ "$MEM_USAGE" -gt 90 ]; then
        notify "WARNING: Memory usage is at ${MEM_USAGE}%"
        
        # Redémarrer les services non critiques
        cd /opt/ohmvision
        docker-compose -f docker-compose.production.yml restart watchtower
    fi
}

# Vérifier la connectivité
check_connectivity() {
    if ! curl -f -k -m 10 https://localhost/health &> /dev/null; then
        notify "CRITICAL: Application health check failed!"
        
        # Restart backend et nginx
        cd /opt/ohmvision
        docker-compose -f docker-compose.production.yml restart backend nginx
        sleep 15
        
        # Revérifier
        if ! curl -f -k -m 10 https://localhost/health &> /dev/null; then
            notify "CRITICAL: Application still unhealthy after restart!"
        else
            log "Application recovered after restart"
        fi
    fi
}

# Vérifier les certificats SSL
check_ssl() {
    CERT_FILE="/opt/ohmvision/docker/ssl/fullchain.pem"
    
    if [ -f "$CERT_FILE" ]; then
        # Vérifier expiration (30 jours)
        EXPIRY_DATE=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
        
        if [ "$DAYS_LEFT" -lt 30 ]; then
            notify "WARNING: SSL certificate expires in $DAYS_LEFT days!"
            
            if [ "$DAYS_LEFT" -lt 7 ]; then
                log "Forcing SSL renewal..."
                cd /opt/ohmvision
                docker-compose -f docker-compose.production.yml exec certbot certbot renew --force-renewal
                docker-compose -f docker-compose.production.yml restart nginx
            fi
        fi
    fi
}

# Vérifier les backups
check_backups() {
    BACKUP_DIR="/opt/ohmvision/backups"
    
    if [ -d "$BACKUP_DIR" ]; then
        # Vérifier qu'il y a un backup récent (moins de 48h)
        LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*.sql" -mtime -2 | head -1)
        
        if [ -z "$LATEST_BACKUP" ]; then
            notify "WARNING: No recent database backup found!"
        fi
    fi
}

# Statistiques
show_stats() {
    log "=== System Stats ==="
    log "CPU: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')"
    log "Memory: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2 }')"
    log "Disk: $(df -h / | awk 'NR==2 {print $5}')"
    log "Uptime: $(uptime -p)"
    
    cd /opt/ohmvision
    log "=== Docker Stats ==="
    docker-compose -f docker-compose.production.yml ps --format "table {{.Service}}\t{{.Status}}"
}

###############################################################################
# MAIN
###############################################################################

main() {
    log "Starting monitoring check..."
    
    check_docker
    check_services
    check_disk_space
    check_memory
    check_connectivity
    check_ssl
    check_backups
    
    # Afficher stats toutes les 12h (si heure = 0 ou 12)
    HOUR=$(date +%H)
    if [ "$HOUR" -eq 0 ] || [ "$HOUR" -eq 12 ]; then
        show_stats
    fi
    
    log "Monitoring check completed"
}

# Exécuter
main

# Cleanup ancien logs (garder 30 jours)
find /var/log -name "ohmvision-monitor.log*" -mtime +30 -delete 2>/dev/null || true
