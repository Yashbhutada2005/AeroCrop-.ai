import React, { useState } from 'react';
import { DiseaseInfo } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { speakText, stopSpeech } from '../../utils/speech';

interface TreatmentCardProps {
  disease: DiseaseInfo;
}

export const TreatmentCard: React.FC<TreatmentCardProps> = ({ disease }) => {
  const { t, language } = useI18n();
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const handleToggleVoice = () => {
    if (isPlayingAudio) {
      stopSpeech();
      setIsPlayingAudio(false);
      return;
    }

    const chem = (disease.chemical_treatment || []).join('. ');
    const org = (disease.organic_treatment || []).join('. ');
    const chemCost = disease.chemical_cost || (disease.is_healthy ? '₹0 / Acre' : '₹550 – ₹900 / Acre');
    const orgCost = disease.organic_cost || (disease.is_healthy ? '₹0 / Acre' : '₹200 – ₹450 / Acre');

    let script = '';
    if (language === 'mr') {
      script = `पिकाचा रोग: ${disease.name}. ${disease.description}. रासायनिक उपाय: ${chem || 'काही नाही'}, रासायनिक अंदाजे खर्च ${chemCost}. सेंद्रिय उपाय: ${org || 'काही नाही'}, सेंद्रिय अंदाजे खर्च ${orgCost}.`;
    } else if (language === 'hi') {
      script = `फसल का रोग: ${disease.name}। ${disease.description}। रासायनिक उपचार: ${chem || 'कोई नहीं'}, रासायनिक अनुमानित लागत ${chemCost}। जैविक उपाय: ${org || 'कोई नहीं'}, जैविक अनुमानित लागत ${orgCost}।`;
    } else {
      script = `Crop Disease: ${disease.name}. ${disease.description}. Chemical treatment: ${chem || 'None'}, estimated cost ${chemCost}. Organic treatment: ${org || 'None'}, estimated cost ${orgCost}.`;
    }

    setIsPlayingAudio(true);
    speakText(
      script,
      language,
      () => setIsPlayingAudio(false),
      () => setIsPlayingAudio(false)
    );
  };

  const chemCostDisplay = disease.chemical_cost || (disease.is_healthy ? '₹0 / Acre' : '₹550 – ₹900 / Acre');
  const orgCostDisplay = disease.organic_cost || (disease.is_healthy ? '₹0 / Acre' : '₹200 – ₹450 / Acre');

  return (
    <div className="card glass treatment-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '8px' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">💊</span>
          <span>{t('treatment_title')}</span>
        </h2>
        <button
          className={`btn btn-sm ${isPlayingAudio ? 'btn-primary' : 'btn-secondary'}`}
          onClick={handleToggleVoice}
          title={isPlayingAudio ? t('voice_stop') : t('voice_listen')}
          aria-label={isPlayingAudio ? t('voice_stop') : t('voice_listen')}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}
        >
          <span>{isPlayingAudio ? '⏹️' : '🔊'}</span>
          <span>{isPlayingAudio ? t('voice_stop') : t('voice_listen')}</span>
        </button>
      </div>

      <p className="disease-desc">
        {disease.description || t('no_desc_avail')}
      </p>

      <div className="treatment-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ margin: 0 }}>⚗️ {t('chemical_treatments')}</h3>
          <span
            className="badge"
            style={{
              background: 'rgba(239, 68, 68, 0.12)',
              color: '#b91c1c',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '0.78rem',
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            💰 {t('treatment_est_cost')}: {chemCostDisplay}
          </span>
        </div>
        <ul className="treatment-list" aria-label="Chemical treatment recommendations">
          {(disease.chemical_treatment && disease.chemical_treatment.length > 0
            ? disease.chemical_treatment
            : [t('no_chem_treatment')]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="treatment-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
          <h3 style={{ margin: 0 }}>🌿 {t('organic_treatments')}</h3>
          <span
            className="badge"
            style={{
              background: 'rgba(22, 163, 74, 0.12)',
              color: '#15803d',
              border: '1px solid rgba(22, 163, 74, 0.3)',
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '0.78rem',
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            🌱 {t('treatment_est_cost')}: {orgCostDisplay}
          </span>
        </div>
        <ul className="treatment-list" aria-label="Organic treatment recommendations">
          {(disease.organic_treatment && disease.organic_treatment.length > 0
            ? disease.organic_treatment
            : [t('no_org_treatment')]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      {!disease.is_healthy && (
        <div
          className="treatment-savings-card glass"
          style={{
            marginTop: '1.25rem',
            padding: '12px 16px',
            borderRadius: '10px',
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.84rem',
            color: 'var(--text-primary)',
          }}
        >
          <span style={{ fontSize: '1.4rem' }}>💡</span>
          <div>
            <strong style={{ color: '#047857' }}>{t('economic_savings_title')}:</strong>{' '}
            {t('economic_savings_tip')}
          </div>
        </div>
      )}
    </div>
  );
};

