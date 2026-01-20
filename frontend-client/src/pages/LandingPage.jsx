import React, { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiActivity, FiShield, FiCpu, FiCheck, FiPlay, FiMail } from 'react-icons/fi';
import { Canvas } from '@react-three/fiber';
import { Hero3D } from '../components/Hero3D';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher';

const LandingPage = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const { t } = useTranslation();

  const handleSubscribe = (e) => {
    e.preventDefault();
    if(email) {
      setSubscribed(true);
      // Logic to send to backend API
      setTimeout(() => setSubscribed(false), 3000); // Reset for demo
      setEmail('');
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 text-white overflow-x-hidden relative">
      {/* Background Ambience */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-ohm-blue/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-ohm-purple/20 rounded-full blur-[120px]" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 glass-panel border-b border-white/5 py-4 px-6 fixed w-full top-0">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-ohm-cyan to-ohm-blue rounded-lg flex items-center justify-center font-bold text-dark-950">
              ⚡
            </div>
            <span className="text-2xl font-bold tracking-tighter">OHM<span className="text-ohm-cyan">VISION</span></span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-medium text-gray-300">
            <a href="#features" className="hover:text-ohm-cyan transition-colors">{t('landing.nav.features')}</a>
            <a href="#security" className="hover:text-ohm-cyan transition-colors">{t('landing.nav.security')}</a>
            <a href="#pricing" className="hover:text-ohm-cyan transition-colors">{t('landing.nav.pricing')}</a>
            <a href="https://www.ohmtronic.fr" target="_blank" rel="noopener noreferrer" className="text-ohm-cyan hover:text-white transition-colors">{t('landing.nav.officialSite')}</a>
          </div>
          <div className="flex gap-4">
            <div className="hidden sm:flex items-center">
              <LanguageSwitcher />
            </div>
            <Link to="/login" className="px-4 py-2 text-sm font-medium hover:text-white text-gray-400 transition-colors">
              {t('landing.nav.login')}
            </Link>
            <Link to="/login" className="px-5 py-2 bg-white/10 hover:bg-ohm-cyan hover:text-dark-900 border border-white/20 rounded-full text-sm font-bold transition-all duration-300 backdrop-blur-sm">
              {t('landing.nav.start')}
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-40 pb-20 px-6">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-ohm-blue/10 border border-ohm-blue/30 text-ohm-cyan text-xs font-bold mb-6 tracking-wide uppercase">
              <span className="w-2 h-2 rounded-full bg-ohm-cyan animate-pulse"></span>
              {t('landing.hero.badge')}
            </div>
            <h1 className="text-5xl lg:text-7xl font-bold leading-tight mb-6">
              {t('landing.hero.titleLine1')} <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-ohm-cyan via-blue-400 to-ohm-purple text-glow">
                {t('landing.hero.titleHighlight')}
              </span>
            </h1>
            <p className="text-xl text-gray-400 mb-8 max-w-xl leading-relaxed">
              {t('landing.hero.subtitle')}
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/login" className="btn-primary flex items-center justify-center gap-2 group">
                {t('landing.hero.ctaDemo')}
                <FiArrowRight className="group-hover:translate-x-1 transition-transform" />
              </Link>
              <button 
                onClick={() => document.getElementById('demo-video').scrollIntoView({ behavior: 'smooth' })}
                className="px-6 py-3 rounded-lg border border-white/20 hover:bg-white/5 transition-all flex items-center justify-center gap-2 font-medium"
              >
                <FiPlay /> {t('landing.hero.ctaTutorial')}
              </button>
            </div>
            
            <div className="mt-12 flex items-center gap-8 text-sm text-gray-500 font-mono">
              <div className="flex items-center gap-2">
                <FiCheck className="text-ohm-cyan" /> {t('landing.hero.kpi1')}
              </div>
              <div className="flex items-center gap-2">
                <FiCheck className="text-ohm-cyan" /> {t('landing.hero.kpi2')}
              </div>
              <div className="flex items-center gap-2">
                <FiCheck className="text-ohm-cyan" /> {t('landing.hero.kpi3')}
              </div>
            </div>
          </motion.div>

          {/* 3D Animation Container */}
          <motion.div 
            className="relative h-[500px] w-full"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
             <div className="absolute inset-0 z-0">
               <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
                  <Suspense fallback={null}>
                    <Hero3D />
                  </Suspense>
               </Canvas>
             </div>
             
             {/* Floating HUD Elements overlaid on 3D */}
             <div className="absolute top-10 right-10 bg-dark-900/50 backdrop-blur border border-ohm-cyan/30 rounded p-4 pointer-events-none">
               <div className="text-xs text-ohm-cyan font-mono mb-1">{t('landing.hero.aiCoreStatus')}</div>
                <div className="text-xl font-bold flex items-center gap-2">
                 {t('landing.hero.aiActive')} <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                </div>
             </div>
          </motion.div>
        </div>
      </section>

      {/* Features Showcase */}
      <section id="features" className="py-24 relative bg-dark-900/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">{t('landing.features.title')} <span className="text-ohm-cyan">{t('landing.features.titleAccent')}</span></h2>
            <p className="text-gray-400 max-w-2xl mx-auto">{t('landing.features.subtitle')}</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<FiCpu className="w-8 h-8 text-ohm-cyan" />}
              title={t('landing.features.card1Title')}
              description={t('landing.features.card1Desc')}
            />
            <FeatureCard 
              icon={<FiActivity className="w-8 h-8 text-ohm-purple" />}
              title={t('landing.features.card2Title')}
              description={t('landing.features.card2Desc')}
            />
            <FeatureCard 
              icon={<FiShield className="w-8 h-8 text-ohm-blue" />}
              title={t('landing.features.card3Title')}
              description={t('landing.features.card3Desc')}
            />
          </div>
        </div>
      </section>

      {/* Tutorial / Learning Section */}
      <section id="demo-video" className="py-20 px-6 max-w-5xl mx-auto text-center">
        <div className="glass-panel rounded-2xl p-8 md:p-12 border border-white/10 relative overflow-hidden">
           <div className="absolute top-0 right-0 p-32 bg-ohm-purple/10 blur-[80px] rounded-full"></div>
           
           <h3 className="text-2xl font-bold mb-6">{t('landing.tutorial.title')}</h3>
           <p className="text-gray-400 mb-8">{t('landing.tutorial.subtitle')}</p>
           
           <div className="aspect-video bg-dark-950 rounded-xl flex items-center justify-center border border-dark-700 group cursor-pointer hover:border-ohm-cyan transition-colors">
              <div className="w-20 h-20 bg-ohm-cyan/20 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <FiPlay className="w-8 h-8 text-ohm-cyan fill-current ml-1" />
              </div>
           </div>
           
           <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm font-mono text-gray-500">
              <div className="p-3 bg-dark-900 rounded border border-dark-800">{t('landing.tutorial.step1')}</div>
              <div className="p-3 bg-dark-900 rounded border border-dark-800">{t('landing.tutorial.step2')}</div>
              <div className="p-3 bg-dark-900 rounded border border-dark-800">{t('landing.tutorial.step3')}</div>
              <div className="p-3 bg-dark-900 rounded border border-dark-800">{t('landing.tutorial.step4')}</div>
           </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-24 relative overflow-hidden">
         <div className="max-w-3xl mx-auto px-6 text-center relative z-10">
            <div className="mb-8 inline-block p-4 rounded-full bg-dark-800/50 backdrop-blur border border-white/10">
               <FiMail className="w-6 h-6 text-ohm-cyan" />
            </div>
            <h2 className="text-4xl font-bold mb-6">{t('landing.newsletter.title')}</h2>
            <p className="text-gray-400 mb-8">{t('landing.newsletter.subtitle')}</p>
            
            <form onSubmit={handleSubscribe} className="relative max-w-md mx-auto">
              <input 
                type="email" 
                placeholder={t('landing.newsletter.emailPlaceholder')} 
                className="w-full pl-6 pr-32 py-4 bg-dark-900/80 border border-dark-700 rounded-full focus:ring-2 focus:ring-ohm-cyan/50 focus:border-ohm-cyan outline-none transition-all text-white placeholder-gray-600"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button 
                type="button" // Disable submit for now in UI only
                onClick={handleSubscribe}
                className="absolute right-2 top-2 bottom-2 px-6 bg-ohm-cyan hover:bg-white text-dark-950 font-bold rounded-full transition-colors flex items-center gap-2"
              >
                {subscribed ? <FiCheck /> : t('landing.newsletter.join')}
              </button>
            </form>
            {subscribed && (
              <motion.p 
                initial={{ opacity: 0, y: 10 }} 
                animate={{ opacity: 1, y: 0 }} 
                className="text-green-400 mt-4 font-medium"
              >
                {t('landing.newsletter.thanks')}
              </motion.p>
            )}
         </div>
         {/* Grid Background */}
         <div className="absolute inset-0 z-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, #232d3f 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
      </section>

      {/* Footer */}
      <footer className="bg-dark-950 border-t border-white/5 pt-16 pb-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
           <div className="text-center md:text-left">
              <div className="text-2xl font-bold mb-2">OHM<span className="text-ohm-cyan">VISION</span></div>
            <p className="text-gray-500 text-sm">{t('landing.footer.copyright')}</p>
           </div>
           <div className="flex gap-6">
            <a href="https://www.ohmtronic.fr" className="text-gray-500 hover:text-ohm-cyan transition-colors">{t('landing.footer.officialSite')}</a>
            <Link to="/legal/privacy" className="text-gray-500 hover:text-ohm-cyan transition-colors">{t('landing.footer.privacy')}</Link>
            <Link to="/legal/gdpr" className="text-gray-500 hover:text-ohm-cyan transition-colors">{t('landing.footer.gdpr')}</Link>
            <Link to="/legal/mentions" className="text-gray-500 hover:text-ohm-cyan transition-colors">{t('landing.footer.mentions')}</Link>
           </div>
        </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, description }) => (
  <div className="glass-card p-8 group hover:-translate-y-2 transition-transform duration-300">
    <div className="mb-6 p-4 rounded-xl bg-dark-800 w-fit border border-white/5 group-hover:border-ohm-cyan/30 transition-colors">
      {icon}
    </div>
    <h3 className="text-xl font-bold mb-3">{title}</h3>
    <p className="text-gray-400 leading-relaxed text-sm">{description}</p>
  </div>
);

export default LandingPage;
