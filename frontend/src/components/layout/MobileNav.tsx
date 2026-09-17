import React, { useState } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { Language } from '../../types';
import { PageTab } from './Sidebar';
import { ProfileModal } from '../auth/ProfileModal';

interface MobileNavProps {
  activeTab: PageTab;
  onTabChange: (tab: PageTab) => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ activeTab, onTabChange }) => {
  const { language, setLanguage, t } = useI18n();
  const { currentUser, isAuthenticated, openAuthModal } = useAuth();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const mobileLabels: Record<Language, Record<PageTab, string>> = {
    en: {
      diagnose: 'Diagnose',
      crops: 'Plots',
      dashboard: 'Dashboard',
      diseases: 'Diseases',
      about: 'About',
    },
    mr: {
      diagnose: 'निदान',
      crops: 'प्लॉट्स',
      dashboard: 'डॅशबोर्ड',
      diseases: 'रोग',
      about: 'माहिती',
    },
    hi: {
      diagnose: 'निदान',
      crops: 'खेत',
      dashboard: 'डैशबोर्ड',
      diseases: 'रोग',
      about: 'जानकारी',
    },
  };

  const navItems: { id: PageTab; icon: string }[] = [
    { id: 'diagnose', icon: '🔬' },
    { id: 'crops', icon: '🌱' },
    { id: 'dashboard', icon: '📊' },
    { id: 'diseases', icon: '🦠' },
    { id: 'about', icon: 'ℹ️' },
  ];

  return (
    <>
      {/* Mobile Top Header */}
      <header className="mobile-header glass" aria-label="Mobile Navigation Bar">
        <div className="mobile-logo" onClick={() => onTabChange('diagnose')}>
          <span className="mobile-logo-icon" aria-hidden="true">🌿</span>
          <span className="mobile-logo-text">AeroCrop<span>.ai</span></span>
        </div>

        {/* Mobile Language Toggle */}
        <div className="mobile-lang-toggle" role="group" aria-label="Language selection">
          {(['en', 'mr', 'hi'] as Language[]).map((l) => (
            <button
              key={l}
              className={`mobile-lang-btn ${language === l ? 'active' : ''}`}
              onClick={() => setLanguage(l)}
              aria-pressed={language === l}
            >
              {l === 'en' ? 'EN' : l === 'mr' ? 'मराठी' : 'हिंदी'}
            </button>
          ))}
        </div>

        {/* Mobile User / Auth Action */}
        <div className="mobile-auth">
          {isAuthenticated ? (
            <button
              className="mobile-avatar-btn"
              onClick={() => setIsProfileModalOpen(true)}
              title={currentUser?.full_name || 'My Profile'}
              aria-label="Open profile settings"
            >
              <span>🌾</span>
              <span className="mobile-status-dot" aria-hidden="true" />
            </button>
          ) : (
            <button
              className="mobile-login-btn"
              onClick={() => openAuthModal('login')}
              aria-label="Sign in"
            >
              <span>👤</span>
              <span className="mobile-login-text">{t('btn_login', 'Login')}</span>
            </button>
          )}
        </div>
      </header>

      {/* Profile Modal for Mobile User */}
      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
      />

      {/* Mobile Bottom Navigation Bar */}
      <nav className="mobile-bottom-nav glass" role="navigation" aria-label="Mobile Bottom Navigation">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          const label = mobileLabels[language]?.[item.id] || mobileLabels.en[item.id];
          return (
            <button
              key={item.id}
              className={`mobile-bottom-item ${isActive ? 'active' : ''}`}
              onClick={() => {
                onTabChange(item.id);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="mobile-item-icon" aria-hidden="true">{item.icon}</span>
              <span className="mobile-item-label">{label}</span>
              {isActive && <span className="mobile-active-indicator" aria-hidden="true" />}
            </button>
          );
        })}
      </nav>
    </>
  );
};
