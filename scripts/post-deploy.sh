#!/bin/bash

###############################################################################
# OHMVISION - POST-DEPLOYMENT SETUP
# Configuration initiale après déploiement sur Hetzner
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
   ____  _   ____  ____     _______  _____ ___  _   __
  / __ \/ | / /  |/  / |   / /  _/ |/ / _ | _ \/ | / /
 / /_/ /  |/ / /|_/ /| |  / // //    / __ |  _/  |/ / 
 \____/_/|_/_/  /_/ |_|__/_/___/_/|_/_/ |_|_| /_/|_/  
                   |_____|                             
  POST-DEPLOYMENT SETUP
EOF
echo -e "${NC}"

###############################################################################
# CONFIGURATION MONITORING
###############################################################################

setup_monitoring() {
    echo -e "${BLUE}Configuration du monitoring automatique...${NC}"
    
    # Rendre le script exécutable
    chmod +x /opt/ohmvision/scripts/monitor.sh
    
    # Ajouter au cron (toutes les 5 minutes)
    (crontab -l 2>/dev/null | grep -v monitor.sh; echo "*/5 * * * * /opt/ohmvision/scripts/monitor.sh") | crontab -
    
    echo -e "${GREEN}✓ Monitoring configuré (toutes les 5 min)${NC}"
}

###############################################################################
# CONFIGURATION BACKUPS
###############################################################################

setup_backups() {
    echo -e "${BLUE}Configuration des backups automatiques...${NC}"
    
    # Créer le répertoire backups
    mkdir -p /opt/ohmvision/backups
    
    # Script de backup
    cat > /opt/ohmvision/scripts/backup.sh << 'EOFBACKUP'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/ohmvision/backups"

cd /opt/ohmvision

# Backup PostgreSQL
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U ohmvision ohmvision > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Backup .env
cp .env $BACKUP_DIR/env_$DATE.bak

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*.bak" -mtime +7 -delete

echo "[$(date)] Backup completed: $DATE"
EOFBACKUP
    
    chmod +x /opt/ohmvision/scripts/backup.sh
    
    # Ajouter au cron (tous les jours à 3h)
    (crontab -l 2>/dev/null | grep -v backup.sh; echo "0 3 * * * /opt/ohmvision/scripts/backup.sh >> /var/log/ohmvision-backup.log 2>&1") | crontab -
    
    echo -e "${GREEN}✓ Backups configurés (tous les jours à 3h)${NC}"
}

###############################################################################
# CONFIGURATION FAIL2BAN
###############################################################################

setup_fail2ban() {
    echo -e "${BLUE}Configuration Fail2Ban...${NC}"
    
    # Configuration Fail2Ban pour Nginx
    cat > /etc/fail2ban/jail.local << 'EOFFAIL2BAN'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
logpath = /opt/ohmvision/logs/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /opt/ohmvision/logs/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /opt/ohmvision/logs/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
logpath = /opt/ohmvision/logs/nginx/access.log
maxretry = 2
EOFFAIL2BAN
    
    # Redémarrer Fail2Ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    echo -e "${GREEN}✓ Fail2Ban configuré${NC}"
}

###############################################################################
# OPTIMISATIONS SYSTÈME
###############################################################################

optimize_system() {
    echo -e "${BLUE}Optimisation du système...${NC}"
    
    # Augmenter les limites de fichiers
    cat >> /etc/security/limits.conf << 'EOFLIMITS'
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOFLIMITS
    
    # Optimisations réseau pour streaming
    cat >> /etc/sysctl.conf << 'EOFSYSCTL'
# OhmVision network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
EOFSYSCTL
    
    sysctl -p
    
    echo -e "${GREEN}✓ Système optimisé${NC}"
}

###############################################################################
# CONFIGURATION SWAP (pour petits serveurs)
###############################################################################

setup_swap() {
    # Vérifier si swap existe déjà
    if [ -f /swapfile ]; then
        echo -e "${YELLOW}Swap déjà configuré${NC}"
        return
    fi
    
    echo -e "${BLUE}Configuration du swap (2GB)...${NC}"
    
    # Créer swap de 2GB
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # Rendre permanent
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    
    # Optimiser swappiness
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    sysctl -p
    
    echo -e "${GREEN}✓ Swap configuré (2GB)${NC}"
}

###############################################################################
# CRÉATION UTILISATEUR NON-ROOT (sécurité)
###############################################################################

create_app_user() {
    echo -e "${BLUE}Création utilisateur application...${NC}"
    
    # Créer utilisateur ohmvision
    if ! id -u ohmvision &>/dev/null; then
        useradd -m -s /bin/bash ohmvision
        usermod -aG docker ohmvision
        
        # Changer propriétaire des fichiers
        chown -R ohmvision:ohmvision /opt/ohmvision
        
        echo -e "${GREEN}✓ Utilisateur 'ohmvision' créé${NC}"
        echo -e "${YELLOW}Pour vous connecter: sudo -u ohmvision -i${NC}"
    else
        echo -e "${YELLOW}Utilisateur 'ohmvision' existe déjà${NC}"
    fi
}

###############################################################################
# AFFICHAGE INFORMATIONS FINALES
###############################################################################

show_info() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          CONFIGURATION POST-DÉPLOIEMENT TERMINÉE!         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Services configurés:${NC}"
    echo "  ✓ Monitoring automatique (toutes les 5 min)"
    echo "  ✓ Backups automatiques (tous les jours à 3h)"
    echo "  ✓ Fail2Ban (protection brute-force)"
    echo "  ✓ Swap 2GB (performance)"
    echo "  ✓ Optimisations système"
    echo ""
    echo -e "${BLUE}Commandes utiles:${NC}"
    echo "  • Monitoring manuel: /opt/ohmvision/scripts/monitor.sh"
    echo "  • Backup manuel: /opt/ohmvision/scripts/backup.sh"
    echo "  • Voir cron jobs: crontab -l"
    echo "  • Fail2Ban status: fail2ban-client status"
    echo ""
    echo -e "${BLUE}Fichiers de logs:${NC}"
    echo "  • Monitoring: /var/log/ohmvision-monitor.log"
    echo "  • Backups: /var/log/ohmvision-backup.log"
    echo "  • Nginx: /opt/ohmvision/logs/nginx/"
    echo ""
    echo -e "${YELLOW}N'oubliez pas:${NC}"
    echo "  1. Configurer WEBHOOK_URL dans /etc/environment pour notifications"
    echo "  2. Tester le backup: /opt/ohmvision/scripts/backup.sh"
    echo "  3. Vérifier le monitoring: tail -f /var/log/ohmvision-monitor.log"
    echo ""
}

###############################################################################
# MAIN
###############################################################################

main() {
    echo -e "${BLUE}Début de la configuration post-déploiement...${NC}"
    echo ""
    
    setup_monitoring
    setup_backups
    setup_fail2ban
    optimize_system
    setup_swap
    create_app_user
    
    show_info
}

# Exécuter
main
