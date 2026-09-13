import { useState } from 'react';
import { api } from '../apiClient';

const sampleMessages = [
  {
    sender: 'M-Money',
    time: '2 min ago',
    preview: "Kanda *182*1*1# kwakira 50,000 RWF byihuse mbere y'uko konti ihagarara. Emeza nonaha...",
    tag: 'danger',
    label: '⚠ High risk · 96%',
  },
  {
    sender: 'MTN MoMo',
    time: '41 min ago',
    preview: 'Wakiriye 12,000 RWF kuri konti yawe ya MoMo. Amafaranga asigaye: 34,500 RWF. Murakoze.',
    tag: 'safe',
    label: '✓ Verified safe',
  },
  {
    sender: '+250 78X XX 210',
    time: '1h ago',
    preview: 'Cher client, votre compte MoMo sera suspendu. Cliquez ici pour confirmer votre identite: bit.ly/mtn-r...',
    tag: 'danger',
    label: '⚠ High risk · 91%',
  },
  {
    sender: 'Unknown',
    time: '3h ago',
    preview: "Muraho, nagusabye guhindura password. Niba atari wowe, ntugire icyo ukora.",
    tag: 'warn',
    label: '? Suspicious · 58%',
  },
];

const gaugeOffset = (score) => {
  const circumference = 452;
  return Math.round(circumference - circumference * score);
};

export default function MobileSimulator() {
  const [activePanel, setActivePanel] = useState('p-home');
  const [messages, setMessages] = useState(sampleMessages);
  const [scan, setScan] = useState(null);
  const [sender, setSender] = useState('');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!sender.trim() || !text.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const result = await api.post('/api/scan', {
        sender: sender.trim(),
        text: text.trim(),
      });

      const preview = result.text_body.length > 80
        ? `${result.text_body.slice(0, 80)}...`
        : result.text_body;

      const isScam = result.fraud_score >= 0.5;
      const tag = isScam ? 'danger' : 'safe';
      const label = `${isScam ? '⚠' : '✓'} ${result.classification} · ${Math.round(result.fraud_score * 100)}%`;

      setMessages((prev) => [
        { sender: result.sender_id, time: 'just now', preview, tag, label },
        ...prev,
      ]);
      setScan(result);
      setActivePanel(isScam ? 'p-alert' : 'p-safe');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setSender('');
      setText('');
    }
  };

  const reportFalsePositive = async () => {
    if (!scan?.scan_id) {
      setScan(null);
      setActivePanel('p-home');
      return;
    }
    try {
      await api.post('/api/feedback', {
        scan_id: scan.scan_id,
        is_false_positive: true,
      });
    } catch (err) {
      console.error('Feedback failed:', err);
    } finally {
      setScan(null);
      setActivePanel('p-home');
    }
  };

  const goHome = () => {
    setScan(null);
    setActivePanel('p-home');
  };

  const currentScan = scan || {
    fraud_score: 0.96,
    text_body: "Kanda *182*1*1# kwakira 50,000 RWF byihuse mbere y'uko konti ihagarara. Emeza nonaha...",
    sender_id: 'M-Money',
    classification: 'Scam',
    engine: 'ml',
  };

  return (
    <div className="mobile-layout">
      <div>
        <div className="phone-shell">
          <div className="phone-notch" />
          <div className="phone-screen">
            <div className="status-row">
              <span>9:41</span>
              <span>MTN RW • 4G 🔋 82%</span>
            </div>
            <div className="app-header">
              <div className="lockup">
                <div className="shield-mark">🛡️</div>
                <div className="name">MoMo <span>Guard</span></div>
              </div>
            </div>
            <div className="phone-body">
              <div className={activePanel === 'p-home' ? 'phone-screen-panel active' : 'phone-screen-panel'} id="p-home">
                <div className="inbox-stat">
                  <div>
                    <div className="num">214</div>
                    <div className="lbl">scanned today</div>
                  </div>
                  <div className="divider" />
                  <div>
                    <div className="num" style={{ color: '#FF6B6B' }}>3</div>
                    <div className="lbl">flagged as scam</div>
                  </div>
                  <div className="divider" />
                  <div>
                    <div className="num" style={{ color: 'var(--mtn-yellow)' }}>211</div>
                    <div className="lbl">verified safe</div>
                  </div>
                </div>
                {messages.map((item, index) => (
                  <div className="sms-card" key={`${item.sender}-${index}`}>
                    <div className="row1">
                      <span className="sms-sender">{item.sender}</span>
                      <span className="sms-time">{item.time}</span>
                    </div>
                    <div className="sms-preview">{item.preview}</div>
                    <span className={`tag ${item.tag}`}>{item.label}</span>
                  </div>
                ))}
              </div>

              <div className={activePanel === 'p-alert' ? 'phone-screen-panel active' : 'phone-screen-panel'} id="p-alert">
                <div className="gauge-wrap">
                  <div className="gauge">
                    <svg width="168" height="168" viewBox="0 0 168 168">
                      <circle cx="84" cy="84" r="72" fill="none" stroke="#F1EFE6" strokeWidth="14" />
                      <circle
                        cx="84" cy="84" r="72" fill="none"
                        stroke="#D6273C" strokeWidth="14" strokeLinecap="round"
                        strokeDasharray="452"
                        strokeDashoffset={gaugeOffset(currentScan.fraud_score)}
                      />
                    </svg>
                    <div className="gauge-center">
                      <div className="pct">{Math.round(currentScan.fraud_score * 100)}%</div>
                      <div className="cap">fraud score</div>
                    </div>
                  </div>
                  <div className="verdict-badge">
                    ⚠ {currentScan.classification?.toUpperCase() || 'SCAM'}
                    {currentScan.engine ? ` · via ${currentScan.engine.toUpperCase()}` : ''}
                  </div>
                </div>

                <div className="msg-block">
                  <div className="from">From: {currentScan.sender_id} · unverified</div>
                  "{currentScan.text_body}"
                </div>

                <div className="reasons">
                  <div className="r-title">Why this was flagged</div>
                  <div className="reason-item">
                    <span className="reason-dot" />Urgency + reward pairing detected.
                  </div>
                  <div className="reason-item">
                    <span className="reason-dot" />Sender ID mimics a payment provider but is not an official MTN shortcode.
                  </div>
                </div>

                <button className="action-btn primary" type="button" onClick={goHome}>
                  Block sender &amp; delete
                </button>
                <button className="action-btn ghost" type="button" onClick={reportFalsePositive}>
                  This isn't a scam — report false positive
                </button>
              </div>

              <div className={activePanel === 'p-safe' ? 'phone-screen-panel active' : 'phone-screen-panel'} id="p-safe">
                <div className="safe-icon">✓</div>
                <div className="safe-title">Verified safe</div>
                <div className="safe-sub">No known threat patterns detected</div>

                <div className="gauge-wrap" style={{ marginTop: 4 }}>
                  <div className="gauge" style={{ width: 168, height: 168 }}>
                    <svg width="168" height="168" viewBox="0 0 168 168">
                      <circle cx="84" cy="84" r="72" fill="none" stroke="#F1EFE6" strokeWidth="14" />
                      <circle
                        cx="84" cy="84" r="72" fill="none"
                        stroke="#0E9F5C" strokeWidth="14" strokeLinecap="round"
                        strokeDasharray="452"
                        strokeDashoffset={gaugeOffset(currentScan.fraud_score)}
                      />
                    </svg>
                    <div className="gauge-center">
                      <div className="pct" style={{ color: 'var(--safe)' }}>{Math.round(currentScan.fraud_score * 100)}%</div>
                      <div className="cap">fraud score</div>
                    </div>
                  </div>
                </div>

                <div className="msg-block" style={{ borderLeftColor: 'var(--safe)' }}>
                  <div className="from">From: {currentScan.sender_id}</div>
                  "{currentScan.text_body}"
                </div>

                <button className="action-btn primary" type="button" onClick={goHome}>
                  Back to inbox
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="annotations">
          <div className="panel">
            <div className="section-head">
              <div className="eyebrow">Receive New SMS</div>
              <h3>Incoming message scanner</h3>
            </div>
            <form onSubmit={handleSubmit} className="input-group">
              <label>Sender</label>
              <input
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                placeholder="e.g. +250 78X XXX XXX"
              />
              <label>Message text</label>
              <textarea
                rows="6"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste the SMS text here..."
              />
              <button className="action-btn primary" type="submit" disabled={loading}>
                {loading ? 'Scanning…' : 'Receive New SMS'}
              </button>
              {error && <p className="note" style={{ color: 'var(--danger)' }}>{error}</p>}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}