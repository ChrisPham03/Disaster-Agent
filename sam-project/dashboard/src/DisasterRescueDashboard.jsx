import React, { useState, useEffect } from "react";
import EmergencyReportForm from "./EmergencyReportForm";

const API_BASE_URL = "http://localhost:5050";

export default function DisasterRescueDashboard() {
  const [victims, setVictims] = useState([]);
  const [rescueTeams, setRescueTeams] = useState([]);
  const [inventory, setInventory] = useState({});
  const [showReportForm, setShowReportForm] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedVictim, setSelectedVictim] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);

  // Update clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
          setConnectionStatus("connected");
          
          // Fetch victims
          const victimsRes = await fetch(`${API_BASE_URL}/api/victim/queue`);
          if (victimsRes.ok) {
            const data = await victimsRes.json();
            setVictims(data.victims || []);
          }

          // Fetch teams
          const teamsRes = await fetch(`${API_BASE_URL}/api/rescue/teams`);
          if (teamsRes.ok) {
            const data = await teamsRes.json();
            setRescueTeams(data.teams || []);
          }

          // Fetch inventory
          const invRes = await fetch(`${API_BASE_URL}/api/resource/inventory`);
          if (invRes.ok) {
            const data = await invRes.json();
            setInventory(data.items || {});
          }
        }
      } catch (err) {
        console.error("API Error:", err);
        setConnectionStatus("offline");
        // Use mock data for demo
        if (victims.length === 0) {
          setVictims([
            {
              victim_id: "V-DEMO1",
              score: 9,
              priority_level: "CRITICAL",
              location: { lat: 13.7563, lng: 100.5018, description: "45 Sukhumvit Road, Bangkok" },
              description: "Building collapse, 5 trapped, fire hazard",
              num_people: 5,
              status: "pending",
            },
            {
              victim_id: "V-DEMO2",
              score: 7,
              priority_level: "URGENT",
              location: { lat: 13.7465, lng: 100.5348, description: "Siam Square" },
              description: "Car accident, 2 injured",
              num_people: 2,
              status: "in_progress",
            },
          ]);
        }
        if (rescueTeams.length === 0) {
          setRescueTeams([
            {
              team_id: "T-Alpha",
              name: "Alpha Response",
              status: "en_route",
              assigned_to: "V-DEMO1",
              location: { lat: 13.7510, lng: 100.5100 },
            },
            {
              team_id: "T-Bravo",
              name: "Bravo Medical",
              status: "available",
              assigned_to: null,
              location: { lat: 13.7480, lng: 100.5320 },
            },
          ]);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [victims.length, rescueTeams.length]);

  const handleReportSuccess = (result) => {
    setSuccessMessage({
      victimId: result.victim_id,
      severity: result.severity_score || 'N/A',
      position: result.queue_position || 'Processing',
    });
    
    setTimeout(() => {
      setShowReportForm(false);
      setSuccessMessage(null);
    }, 3000);
  };

  const getSeverityColor = (score) => {
    if (score >= 9) return "#ff1744";
    if (score >= 7) return "#ff9100";
    if (score >= 5) return "#ffea00";
    return "#69f0ae";
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "#ff1744",
      in_progress: "#00e5ff",
      resolved: "#69f0ae",
      available: "#69f0ae",
      en_route: "#ff9100",
      on_scene: "#00e5ff",
    };
    return colors[status] || "#8892b0";
  };

  const criticalCount = victims.filter((v) => v.score >= 9).length;
  const urgentCount = victims.filter((v) => v.score >= 7 && v.score < 9).length;
  const activeTeams = rescueTeams.filter((t) => t.status !== "available").length;

  return (
    <div style={styles.container}>
      {/* Scanline effect */}
      <div style={styles.scanlines} />

      {/* Emergency Form Modal */}
      {showReportForm && (
        <EmergencyReportForm
          onSuccess={handleReportSuccess}
          onClose={() => setShowReportForm(false)}
        />
      )}

      {/* Success Toast */}
      {successMessage && (
        <div style={styles.successToast}>
          <div style={styles.successIcon}>✓</div>
          <div>
            <div style={styles.successTitle}>REPORT SUBMITTED</div>
            <div style={styles.successText}>
              Victim {successMessage.victimId} • Severity: {successMessage.severity}/10 • Queue: #{successMessage.position}
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logoIcon}>⚡</div>
          <div>
            <h1 style={styles.title}>DISASTER RESPONSE</h1>
            <p style={styles.subtitle}>COMMAND CENTER v2.0</p>
          </div>
        </div>

        <div style={styles.headerCenter}>
          <div style={styles.criticalBadge}>
            <span style={styles.pulsingDot} />
            <span>{criticalCount} CRITICAL</span>
          </div>
          <div style={styles.urgentBadge}>
            <span>{urgentCount} URGENT</span>
          </div>
          <div style={styles.teamsBadge}>
            <span>{activeTeams}/{rescueTeams.length} TEAMS ACTIVE</span>
          </div>
        </div>

        <div style={styles.headerRight}>
          <div style={styles.clockContainer}>
            <div style={styles.clockLabel}>SYSTEM TIME</div>
            <div style={styles.clock}>
              {currentTime.toLocaleTimeString("en-US", { hour12: false })}
            </div>
          </div>
          <div style={{
            ...styles.connectionBadge,
            borderColor: connectionStatus === 'connected' ? '#69f0ae' : '#ff9100',
          }}>
            <span style={{
              ...styles.connectionDot,
              background: connectionStatus === 'connected' ? '#69f0ae' : '#ff9100',
            }} />
            {connectionStatus.toUpperCase()}
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav style={styles.nav}>
        <button
          onClick={() => setShowReportForm(true)}
          style={styles.addReportButton}
        >
          ➕ NEW EMERGENCY REPORT
        </button>
      </nav>

      {/* Main Content: Map + Queue */}
      <main style={styles.main}>
        <div style={styles.splitLayout}>
          {/* LEFT: MAP */}
          <div style={styles.mapSection}>
            <div style={styles.mapHeader}>
              <span>🗺️ LIVE SITUATION MAP</span>
              <span style={styles.mapStats}>
                {victims.length} INCIDENTS • {rescueTeams.length} TEAMS
              </span>
            </div>
            <div style={styles.mapContent}>
              <svg style={styles.mapSvg} viewBox="0 0 400 300">
                {/* Grid lines */}
                {[...Array(11)].map((_, i) => (
                  <line
                    key={`h${i}`}
                    x1="0"
                    y1={i * 30}
                    x2="400"
                    y2={i * 30}
                    stroke="#1a3a4a"
                    strokeWidth="1"
                  />
                ))}
                {[...Array(14)].map((_, i) => (
                  <line
                    key={`v${i}`}
                    x1={i * 30}
                    y1="0"
                    x2={i * 30}
                    y2="300"
                    stroke="#1a3a4a"
                    strokeWidth="1"
                  />
                ))}

                {/* Victims - Circles */}
                {victims.map((v, idx) => {
                  const x = 50 + (idx % 4) * 90;
                  const y = 60 + Math.floor(idx / 4) * 80;
                  const color = getSeverityColor(v.score);
                  
                  return (
                    <g key={v.victim_id}>
                      {/* Pulse effect for critical */}
                      {v.score >= 9 && (
                        <circle 
                          cx={x} 
                          cy={y} 
                          r="20" 
                          fill="none" 
                          stroke={color} 
                          strokeWidth="2" 
                          opacity="0.5"
                        >
                          <animate 
                            attributeName="r" 
                            from="15" 
                            to="30" 
                            dur="1.5s" 
                            repeatCount="indefinite" 
                          />
                          <animate 
                            attributeName="opacity" 
                            from="0.8" 
                            to="0" 
                            dur="1.5s" 
                            repeatCount="indefinite" 
                          />
                        </circle>
                      )}
                      
                      {/* Main circle */}
                      <circle
                        cx={x}
                        cy={y}
                        r="12"
                        fill={color}
                        stroke="#0a0a0f"
                        strokeWidth="3"
                        style={{ cursor: "pointer" }}
                        onClick={() => setSelectedVictim(v)}
                      />
                      
                      {/* Score text */}
                      <text 
                        x={x} 
                        y={y + 4} 
                        fill="#0a0a0f" 
                        fontSize="10" 
                        fontWeight="bold" 
                        textAnchor="middle"
                      >
                        {v.score}
                      </text>
                      
                      {/* ID label */}
                      <text 
                        x={x} 
                        y={y + 28} 
                        fill="#8892b0" 
                        fontSize="8" 
                        textAnchor="middle"
                      >
                        {v.victim_id.slice(0, 8)}
                      </text>
                    </g>
                  );
                })}

                {/* Rescue Teams - Squares */}
                {rescueTeams.map((t, idx) => {
                  const x = 80 + idx * 90;
                  const y = 240;
                  const color = t.status === "available" ? "#69f0ae" : "#00e5ff";
                  
                  // Draw line to assigned victim
                  const assignedVictimIdx = victims.findIndex((v) => v.victim_id === t.assigned_to);
                  
                  return (
                    <g key={t.team_id}>
                      {/* Connection line */}
                      {t.assigned_to && assignedVictimIdx >= 0 && (
                        <line
                          x1={x}
                          y1={y}
                          x2={50 + (assignedVictimIdx % 4) * 90}
                          y2={60 + Math.floor(assignedVictimIdx / 4) * 80}
                          stroke="#00e5ff"
                          strokeWidth="2"
                          strokeDasharray="5,5"
                          opacity="0.6"
                        >
                          <animate 
                            attributeName="stroke-dashoffset" 
                            from="0" 
                            to="-10" 
                            dur="0.5s" 
                            repeatCount="indefinite" 
                          />
                        </line>
                      )}
                      
                      {/* Team square */}
                      <rect
                        x={x - 15}
                        y={y - 10}
                        width="30"
                        height="20"
                        fill={color}
                        stroke="#0a0a0f"
                        strokeWidth="2"
                        rx="3"
                        style={{ cursor: "pointer" }}
                        onClick={() => setSelectedTeam(t)}
                      />
                      
                      {/* Team ID */}
                      <text 
                        x={x} 
                        y={y + 4} 
                        fill="#0a0a0f" 
                        fontSize="8" 
                        fontWeight="bold" 
                        textAnchor="middle"
                      >
                        {t.team_id.slice(-1)}
                      </text>
                    </g>
                  );
                })}
              </svg>

              {/* Map Legend */}
              <div style={styles.mapLegend}>
                <div style={styles.legendItem}>
                  <span style={{ ...styles.legendCircle, background: "#ff1744" }} />
                  CRITICAL (9-10)
                </div>
                <div style={styles.legendItem}>
                  <span style={{ ...styles.legendCircle, background: "#ff9100" }} />
                  URGENT (7-8)
                </div>
                <div style={styles.legendItem}>
                  <span style={{ ...styles.legendSquare, background: "#69f0ae" }} />
                  TEAM AVAILABLE
                </div>
                <div style={styles.legendItem}>
                  <span style={{ ...styles.legendSquare, background: "#00e5ff" }} />
                  TEAM DEPLOYED
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT: PRIORITY QUEUE */}
          <div style={styles.queueSection}>
            <div style={styles.queueHeader}>
              <span>📋 PRIORITY QUEUE</span>
              <span style={styles.queueCount}>{victims.length} TOTAL</span>
            </div>
            
            <div style={styles.queueContent}>
              {victims.length === 0 ? (
                <div style={styles.emptyState}>
                  <div style={styles.emptyIcon}>📭</div>
                  <p style={styles.emptyText}>No Active Emergencies</p>
                  <p style={styles.emptySubtext}>
                    Click "NEW EMERGENCY REPORT" to submit
                  </p>
                </div>
              ) : (
                victims
                  .sort((a, b) => b.score - a.score)
                  .map((victim, index) => (
                    <div
                      key={victim.victim_id}
                      style={{
                        ...styles.queueItem,
                        borderLeftColor: getSeverityColor(victim.score),
                        ...(selectedVictim?.victim_id === victim.victim_id ? styles.queueItemSelected : {})
                      }}
                      onClick={() => setSelectedVictim(victim)}
                    >
                      <div style={styles.queueRank}>#{index + 1}</div>
                      <div style={styles.queueMain}>
                        <div style={styles.queueTop}>
                          <span style={styles.queueId}>{victim.victim_id}</span>
                          <span style={{
                            ...styles.queueSeverity,
                            background: getSeverityColor(victim.score)
                          }}>
                            {victim.score}/10
                          </span>
                          <span style={styles.queueLevel}>{victim.priority_level}</span>
                        </div>
                        <div style={styles.queueDesc}>{victim.description}</div>
                        <div style={styles.queueMeta}>
                          <span>📍 {victim.location?.description || 'Unknown'}</span>
                          <span>👥 {victim.num_people}</span>
                          <span style={{ color: getStatusColor(victim.status) }}>
                            {victim.status?.toUpperCase().replace("_", " ")}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
              )}
            </div>

            {/* Selected Victim Details */}
            {selectedVictim && (
              <div style={styles.detailPanel}>
                <div style={styles.detailHeader}>
                  <span>SELECTED: {selectedVictim.victim_id}</span>
                  <button onClick={() => setSelectedVictim(null)} style={styles.detailClose}>
                    ✕
                  </button>
                </div>
                <div style={styles.detailContent}>
                  <div style={styles.detailRow}>
                    <span style={styles.detailLabel}>SEVERITY</span>
                    <span style={{
                      ...styles.detailBadge,
                      background: getSeverityColor(selectedVictim.score)
                    }}>
                      {selectedVictim.score}/10 - {selectedVictim.priority_level}
                    </span>
                  </div>
                  <div style={styles.detailRow}>
                    <span style={styles.detailLabel}>LOCATION</span>
                    <span style={styles.detailValue}>
                      {selectedVictim.location?.description}
                    </span>
                  </div>
                  <div style={styles.detailRow}>
                    <span style={styles.detailLabel}>PEOPLE</span>
                    <span style={styles.detailValue}>{selectedVictim.num_people}</span>
                  </div>
                  <div style={styles.detailRow}>
                    <span style={styles.detailLabel}>STATUS</span>
                    <span style={{ ...styles.detailValue, color: getStatusColor(selectedVictim.status) }}>
                      {selectedVictim.status?.toUpperCase().replace("_", " ")}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Selected Team Details */}
            {selectedTeam && (
              <div style={styles.detailPanel}>
                <div style={styles.detailHeader}>
                  <span>TEAM: {selectedTeam.team_id}</span>
                  <button onClick={() => setSelectedTeam(null)} style={styles.detailClose}>
                    ✕
                  </button>
                </div>
                <div style={styles.detailContent}>
                  <div style={styles.detailRow}>
                    <span style={styles.detailLabel}>NAME</span>
                    <span style={styles.detailValue}>{selectedTeam.name}</span>
                  </div>
                  <div style={styles.detailRow}>
                    <span style={styles.detailLabel}>STATUS</span>
                    <span style={{ ...styles.detailValue, color: getStatusColor(selectedTeam.status) }}>
                      {selectedTeam.status?.toUpperCase().replace("_", " ")}
                    </span>
                  </div>
                  {selectedTeam.assigned_to && (
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>ASSIGNED TO</span>
                      <span style={{ ...styles.detailValue, color: "#00e5ff" }}>
                        {selectedTeam.assigned_to}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <div>SOLACE AGENT MESH • DISASTER RESPONSE SYSTEM</div>
        <div style={styles.footerCenter}>REST API: {API_BASE_URL}</div>
        <div>© 2026 Emergency Response Command</div>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%)",
    color: "#e6e6e6",
    fontFamily: "'JetBrains Mono', 'Courier New', monospace",
    position: "relative",
  },
  
  scanlines: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,229,255,0.03) 2px, rgba(0,229,255,0.03) 4px)",
    pointerEvents: "none",
    zIndex: 1000,
  },
  
  // Success Toast
  successToast: {
    position: "fixed",
    top: "100px",
    right: "24px",
    background: "#1a1a2e",
    border: "2px solid #69f0ae",
    borderRadius: "8px",
    padding: "20px",
    display: "flex",
    alignItems: "center",
    gap: "16px",
    zIndex: 4000,
    minWidth: "400px",
    boxShadow: "0 10px 40px rgba(105, 240, 174, 0.3)",
  },
  successIcon: {
    fontSize: "32px",
    color: "#69f0ae",
    background: "rgba(105, 240, 174, 0.2)",
    borderRadius: "50%",
    width: "50px",
    height: "50px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  successTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#69f0ae",
    letterSpacing: "1px",
    marginBottom: "4px",
  },
  successText: {
    fontSize: "12px",
    color: "#e6e6e6",
  },
  
  // Header
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 24px",
    borderBottom: "1px solid #1a3a4a",
    background: "rgba(10, 10, 15, 0.95)",
    backdropFilter: "blur(10px)",
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  logoIcon: {
    fontSize: "32px",
    background: "linear-gradient(135deg, #00e5ff, #64ffda)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  title: {
    fontSize: "20px",
    fontWeight: 700,
    color: "#00e5ff",
    margin: 0,
    letterSpacing: "2px",
  },
  subtitle: {
    fontSize: "10px",
    color: "#64ffda",
    margin: 0,
    letterSpacing: "4px",
  },
  headerCenter: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
  },
  criticalBadge: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    background: "rgba(255, 23, 68, 0.2)",
    border: "1px solid #ff1744",
    padding: "8px 16px",
    borderRadius: "4px",
    fontSize: "12px",
    fontWeight: 600,
    color: "#ff1744",
  },
  pulsingDot: {
    width: "8px",
    height: "8px",
    background: "#ff1744",
    borderRadius: "50%",
    animation: "pulse 1s infinite",
  },
  urgentBadge: {
    background: "rgba(255, 145, 0, 0.2)",
    border: "1px solid #ff9100",
    padding: "8px 16px",
    borderRadius: "4px",
    fontSize: "12px",
    fontWeight: 600,
    color: "#ff9100",
  },
  teamsBadge: {
    background: "rgba(0, 229, 255, 0.2)",
    border: "1px solid #00e5ff",
    padding: "8px 16px",
    borderRadius: "4px",
    fontSize: "12px",
    fontWeight: 600,
    color: "#00e5ff",
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: "20px",
  },
  clockContainer: {
    textAlign: "right",
  },
  clockLabel: {
    fontSize: "9px",
    color: "#64ffda",
    letterSpacing: "2px",
  },
  clock: {
    fontSize: "24px",
    fontWeight: 700,
    color: "#00e5ff",
  },
  connectionBadge: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    padding: "6px 12px",
    border: "1px solid",
    borderRadius: "4px",
    fontSize: "10px",
    fontWeight: 600,
  },
  connectionDot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
  },
  
  // Navigation
  nav: {
    display: "flex",
    justifyContent: "flex-end",
    padding: "8px 24px",
    borderBottom: "1px solid #1a3a4a",
    background: "rgba(13, 17, 23, 0.8)",
  },
  addReportButton: {
    padding: "10px 20px",
    background: "rgba(105, 240, 174, 0.2)",
    border: "1px solid #69f0ae",
    borderRadius: "4px",
    color: "#69f0ae",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    fontFamily: "inherit",
    transition: "all 0.2s",
  },
  
  // Main Split Layout
  main: {
    padding: "20px 24px",
    minHeight: "calc(100vh - 200px)",
  },
  splitLayout: {
    display: "grid",
    gridTemplateColumns: "1fr 500px",
    gap: "20px",
    height: "calc(100vh - 240px)",
  },
  
  // Map Section (Left)
  mapSection: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
  },
  mapHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    borderBottom: "1px solid #1a3a4a",
    fontSize: "12px",
    fontWeight: 600,
    color: "#64ffda",
    letterSpacing: "1px",
  },
  mapStats: {
    color: "#8892b0",
  },
  mapContent: {
    flex: 1,
    padding: "20px",
    display: "flex",
    flexDirection: "column",
  },
  mapSvg: {
    flex: 1,
    background: "#0a0a0f",
    borderRadius: "4px",
    border: "1px solid #1a3a4a",
  },
  mapLegend: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
    marginTop: "16px",
    padding: "12px",
    background: "rgba(26, 58, 74, 0.3)",
    borderRadius: "4px",
  },
  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    fontSize: "10px",
    color: "#8892b0",
  },
  legendCircle: {
    width: "12px",
    height: "12px",
    borderRadius: "50%",
  },
  legendSquare: {
    width: "12px",
    height: "12px",
    borderRadius: "2px",
  },
  
  // Queue Section (Right)
  queueSection: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  queueHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    fontSize: "12px",
    fontWeight: 600,
    color: "#64ffda",
    letterSpacing: "1px",
  },
  queueCount: {
    color: "#8892b0",
  },
  queueContent: {
    flex: 1,
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "auto",
    maxHeight: "calc(100vh - 400px)",
  },
  emptyState: {
    padding: "60px 20px",
    textAlign: "center",
    color: "#8892b0",
  },
  emptyIcon: {
    fontSize: "48px",
    marginBottom: "16px",
  },
  emptyText: {
    fontSize: "14px",
    fontWeight: 600,
    marginBottom: "8px",
  },
  emptySubtext: {
    fontSize: "11px",
    color: "#64ffda",
  },
  queueItem: {
    display: "flex",
    gap: "12px",
    padding: "12px 16px",
    borderBottom: "1px solid #1a3a4a",
    borderLeft: "4px solid",
    cursor: "pointer",
    transition: "background 0.2s",
  },
  queueItemSelected: {
    background: "rgba(0, 229, 255, 0.1)",
  },
  queueRank: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#8892b0",
    minWidth: "30px",
  },
  queueMain: {
    flex: 1,
  },
  queueTop: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "6px",
  },
  queueId: {
    fontSize: "11px",
    color: "#00e5ff",
    fontWeight: 600,
  },
  queueSeverity: {
    padding: "2px 6px",
    borderRadius: "3px",
    fontSize: "9px",
    fontWeight: 700,
    color: "#0a0a0f",
  },
  queueLevel: {
    fontSize: "9px",
    color: "#ff9100",
    fontWeight: 600,
    letterSpacing: "0.5px",
  },
  queueDesc: {
    fontSize: "11px",
    color: "#e6e6e6",
    marginBottom: "6px",
    lineHeight: 1.4,
  },
  queueMeta: {
    display: "flex",
    gap: "12px",
    fontSize: "10px",
    color: "#8892b0",
  },
  
  // Detail Panel
  detailPanel: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
  },
  detailHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 12px",
    borderBottom: "1px solid #1a3a4a",
    fontSize: "10px",
    fontWeight: 600,
    color: "#64ffda",
    letterSpacing: "1px",
  },
  detailClose: {
    background: "transparent",
    border: "none",
    color: "#8892b0",
    fontSize: "14px",
    cursor: "pointer",
    padding: "4px",
  },
  detailContent: {
    padding: "12px",
  },
  detailRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },
  detailLabel: {
    fontSize: "9px",
    color: "#8892b0",
    letterSpacing: "1px",
  },
  detailValue: {
    fontSize: "11px",
    color: "#e6e6e6",
    fontWeight: 500,
  },
  detailBadge: {
    padding: "3px 8px",
    borderRadius: "3px",
    fontSize: "9px",
    fontWeight: 700,
    color: "#0a0a0f",
  },
  
  // Footer
  footer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 24px",
    borderTop: "1px solid #1a3a4a",
    background: "rgba(10, 10, 15, 0.95)",
    fontSize: "10px",
    color: "#8892b0",
    letterSpacing: "1px",
  },
  footerCenter: {
    color: "#64ffda",
  },
};

// Add CSS animation
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;
if (!document.querySelector('style[data-dashboard-styles]')) {
  styleSheet.setAttribute('data-dashboard-styles', 'true');
  document.head.appendChild(styleSheet);
}