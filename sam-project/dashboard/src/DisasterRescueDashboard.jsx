import React, { useState, useEffect, useCallback } from "react";

// API configuration - adjust to match your REST gateway
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5050";

// Fallback mock data for when API is unavailable
const MOCK_VICTIMS = [
  {
    victim_id: "V-8a3f2c1d",
    score: 9,
    priority_level: "CRITICAL",
    location: { lat: 13.7563, lng: 100.5018, description: "45 Sukhumvit Road, Bangkok" },
    description: "Building collapse, 5 trapped, 2 children, fire hazard",
    num_people: 5,
    status: "pending",
    color_code: "red",
    timestamp: new Date(Date.now() - 300000).toISOString(),
  },
  {
    victim_id: "V-7b4e3d2c",
    score: 7,
    priority_level: "URGENT",
    location: { lat: 13.7465, lng: 100.5348, description: "Siam Square, Bangkok" },
    description: "Car accident, 2 injured, one with fracture",
    num_people: 2,
    status: "in_progress",
    color_code: "orange",
    timestamp: new Date(Date.now() - 600000).toISOString(),
  },
];

const MOCK_RESCUE_TEAMS = [
  {
    team_id: "T-Alpha",
    name: "Alpha Response Unit",
    location: { lat: 13.7510, lng: 100.5100 },
    status: "en_route",
    assigned_to: "V-8a3f2c1d",
    eta_minutes: 8,
    personnel: 6,
    vehicle: "Heavy Rescue Truck",
  },
  {
    team_id: "T-Bravo",
    name: "Bravo Medical Team",
    location: { lat: 13.7480, lng: 100.5320 },
    status: "available",
    assigned_to: null,
    eta_minutes: null,
    personnel: 4,
    vehicle: "Ambulance Unit",
  },
];

const MOCK_INVENTORY = {
  stretcher: { total: 15, available: 10, allocated: 5 },
  first_aid_kit: { total: 50, available: 42, allocated: 8 },
  hydraulic_cutter: { total: 4, available: 2, allocated: 2 },
  oxygen_tank: { total: 20, available: 15, allocated: 5 },
};

/**
 * API Client for backend communication
 */
const apiClient = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },
  
  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
};

export default function DisasterRescueDashboard() {
  const [victims, setVictims] = useState([]);
  const [rescueTeams, setRescueTeams] = useState([]);
  const [inventory, setInventory] = useState({});
  const [selectedVictim, setSelectedVictim] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [activeTab, setActiveTab] = useState("map");
  const [error, setError] = useState(null);
  
  // New victim report form state
  const [showReportForm, setShowReportForm] = useState(false);
  const [reportForm, setReportForm] = useState({
    location: '',
    latitude: '',
    longitude: '',
    description: '',
    num_people: 1,
  });
  const [submitting, setSubmitting] = useState(false);

  // Update clock every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch data from backend
  const fetchData = useCallback(async () => {
    try {
      // Try to fetch from real API
      const [victimsRes, teamsRes, inventoryRes] = await Promise.allSettled([
        apiClient.get('/api/victim/queue'),
        apiClient.get('/api/rescue/teams'),
        apiClient.get('/api/resource/inventory'),
      ]);

      let apiConnected = false;

      // Process victims response
      if (victimsRes.status === 'fulfilled' && victimsRes.value) {
        const victimsData = victimsRes.value.victims || victimsRes.value || [];
        if (Array.isArray(victimsData)) {
          setVictims(victimsData);
          apiConnected = true;
        }
      }

      // Process teams response
      if (teamsRes.status === 'fulfilled' && teamsRes.value) {
        const teamsData = teamsRes.value.teams || teamsRes.value || [];
        if (Array.isArray(teamsData)) {
          setRescueTeams(teamsData);
          apiConnected = true;
        }
      }

      // Process inventory response
      if (inventoryRes.status === 'fulfilled' && inventoryRes.value) {
        const invData = inventoryRes.value.items || inventoryRes.value || {};
        if (typeof invData === 'object') {
          setInventory(invData);
          apiConnected = true;
        }
      }

      setConnectionStatus(apiConnected ? "connected" : "demo");
      setError(null);
      
      // Fall back to mock data if no API data received
      if (!apiConnected) {
        if (victims.length === 0) setVictims(MOCK_VICTIMS);
        if (rescueTeams.length === 0) setRescueTeams(MOCK_RESCUE_TEAMS);
        if (Object.keys(inventory).length === 0) setInventory(MOCK_INVENTORY);
      }

    } catch (err) {
      console.error("API fetch error:", err);
      setConnectionStatus("offline");
      setError(err.message);
      
      // Use mock data on error
      if (victims.length === 0) setVictims(MOCK_VICTIMS);
      if (rescueTeams.length === 0) setRescueTeams(MOCK_RESCUE_TEAMS);
      if (Object.keys(inventory).length === 0) setInventory(MOCK_INVENTORY);
    }
  }, [victims.length, rescueTeams.length, inventory]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, [fetchData]);

  // Submit new victim report
  const handleSubmitReport = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const payload = {
        location: reportForm.location,
        latitude: reportForm.latitude ? parseFloat(reportForm.latitude) : null,
        longitude: reportForm.longitude ? parseFloat(reportForm.longitude) : null,
        description: reportForm.description,
        num_people: parseInt(reportForm.num_people) || 1,
      };
      
      const result = await apiClient.post('/api/victim/report', payload);
      
      if (result.status === 'success' || result.victim_id) {
        alert(`Report submitted successfully! Victim ID: ${result.victim_id || 'assigned'}`);
        setShowReportForm(false);
        setReportForm({ location: '', latitude: '', longitude: '', description: '', num_people: 1 });
        fetchData(); // Refresh the data
      } else {
        alert(`Report status: ${result.message || JSON.stringify(result)}`);
      }
    } catch (err) {
      console.error("Submit error:", err);
      alert(`Failed to submit report: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  // Assign team to victim
  const handleAssignTeam = async (teamId, victimId) => {
    try {
      const victim = victims.find(v => v.victim_id === victimId);
      const result = await apiClient.post('/api/rescue/assign', {
        team_id: teamId,
        victim_id: victimId,
        victim_location: victim?.location || null,
      });
      
      if (result.status === 'success') {
        alert(`Team ${teamId} assigned to ${victimId}. ETA: ${result.eta_minutes} minutes`);
        fetchData();
      } else {
        alert(`Assignment failed: ${result.message}`);
      }
    } catch (err) {
      alert(`Failed to assign team: ${err.message}`);
    }
  };

  // Update victim status
  const handleUpdateVictimStatus = async (victimId, newStatus) => {
    try {
      const result = await apiClient.post('/api/victim/status', {
        victim_id: victimId,
        status: newStatus,
      });
      
      if (result.status === 'success') {
        fetchData();
      }
    } catch (err) {
      console.error("Status update error:", err);
    }
  };

  const getSeverityColor = (score) => {
    if (score >= 9) return "#ff1744";
    if (score >= 7) return "#ff9100";
    if (score >= 5) return "#ffea00";
    return "#69f0ae";
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: { bg: "#1a1a2e", border: "#ff1744", text: "#ff1744" },
      in_progress: { bg: "#1a1a2e", border: "#00e5ff", text: "#00e5ff" },
      resolved: { bg: "#1a1a2e", border: "#69f0ae", text: "#69f0ae" },
      available: { bg: "#1a1a2e", border: "#69f0ae", text: "#69f0ae" },
      en_route: { bg: "#1a1a2e", border: "#ff9100", text: "#ff9100" },
      on_scene: { bg: "#1a1a2e", border: "#00e5ff", text: "#00e5ff" },
    };
    return styles[status] || styles.pending;
  };

  const formatTime = (isoString) => {
    if (!isoString) return "Unknown";
    const date = new Date(isoString);
    const mins = Math.floor((Date.now() - date) / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m ago`;
  };

  const criticalCount = victims.filter((v) => v.score >= 9).length;
  const urgentCount = victims.filter((v) => v.score >= 7 && v.score < 9).length;
  const activeTeams = rescueTeams.filter((t) => t.status !== "available").length;
  const availableTeams = rescueTeams.filter((t) => t.status === "available");

  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected': return '#69f0ae';
      case 'demo': return '#ff9100';
      default: return '#ff1744';
    }
  };

  return (
    <div style={styles.container}>
      {/* Scanline overlay effect */}
      <div style={styles.scanlines} />

      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logoContainer}>
            <div style={styles.logoIcon}>⚡</div>
            <div>
              <h1 style={styles.title}>DISASTER RESPONSE</h1>
              <p style={styles.subtitle}>COMMAND CENTER v2.0</p>
            </div>
          </div>
        </div>

        <div style={styles.headerCenter}>
          <div style={styles.statusIndicators}>
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
        </div>

        <div style={styles.headerRight}>
          <div style={styles.clockContainer}>
            <div style={styles.clockLabel}>SYSTEM TIME</div>
            <div style={styles.clock}>
              {currentTime.toLocaleTimeString("en-US", { hour12: false })}
            </div>
            <div style={styles.dateDisplay}>
              {currentTime.toLocaleDateString("en-US", {
                weekday: "short",
                month: "short",
                day: "numeric",
              })}
            </div>
          </div>
          <div
            style={{
              ...styles.connectionBadge,
              borderColor: getConnectionColor(),
            }}
          >
            <span
              style={{
                ...styles.connectionDot,
                background: getConnectionColor(),
              }}
            />
            {connectionStatus.toUpperCase()}
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav style={styles.nav}>
        {["map", "queue", "teams", "resources"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...styles.navButton,
              ...(activeTab === tab ? styles.navButtonActive : {}),
            }}
          >
            {tab === "map" && "🗺️ "}
            {tab === "queue" && "📋 "}
            {tab === "teams" && "🚑 "}
            {tab === "resources" && "📦 "}
            {tab.toUpperCase()}
          </button>
        ))}
        
        {/* Add Report Button */}
        <button
          onClick={() => setShowReportForm(true)}
          style={styles.addReportButton}
        >
          ➕ NEW REPORT
        </button>
      </nav>

      {/* Error Banner */}
      {error && connectionStatus === 'offline' && (
        <div style={styles.errorBanner}>
          ⚠️ API Connection Error: {error} - Using demo data
        </div>
      )}

      {/* New Report Modal */}
      {showReportForm && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <div style={styles.modalHeader}>
              <h2 style={styles.modalTitle}>📞 NEW EMERGENCY REPORT</h2>
              <button onClick={() => setShowReportForm(false)} style={styles.closeButton}>✕</button>
            </div>
            <form onSubmit={handleSubmitReport} style={styles.form}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Location Description *</label>
                <input
                  type="text"
                  value={reportForm.location}
                  onChange={(e) => setReportForm({...reportForm, location: e.target.value})}
                  placeholder="e.g., 45 Sukhumvit Road, Bangkok"
                  style={styles.input}
                  required
                />
              </div>
              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Latitude</label>
                  <input
                    type="number"
                    step="any"
                    value={reportForm.latitude}
                    onChange={(e) => setReportForm({...reportForm, latitude: e.target.value})}
                    placeholder="13.7563"
                    style={styles.input}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={reportForm.longitude}
                    onChange={(e) => setReportForm({...reportForm, longitude: e.target.value})}
                    placeholder="100.5018"
                    style={styles.input}
                  />
                </div>
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Situation Description *</label>
                <textarea
                  value={reportForm.description}
                  onChange={(e) => setReportForm({...reportForm, description: e.target.value})}
                  placeholder="Describe the emergency situation, injuries, hazards..."
                  style={styles.textarea}
                  required
                />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Number of People *</label>
                <input
                  type="number"
                  min="1"
                  value={reportForm.num_people}
                  onChange={(e) => setReportForm({...reportForm, num_people: e.target.value})}
                  style={styles.input}
                  required
                />
              </div>
              <div style={styles.formActions}>
                <button type="button" onClick={() => setShowReportForm(false)} style={styles.cancelButton}>
                  Cancel
                </button>
                <button type="submit" disabled={submitting} style={styles.submitButton}>
                  {submitting ? 'Submitting...' : '🚨 Submit Emergency Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main style={styles.main}>
        {activeTab === "map" && (
          <div style={styles.mapLayout}>
            {/* Map Panel */}
            <div style={styles.mapContainer}>
              <div style={styles.mapHeader}>
                <span>LIVE SITUATION MAP</span>
                <span style={styles.mapCoords}>
                  {victims.length} INCIDENTS | {rescueTeams.length} TEAMS
                </span>
              </div>
              <div style={styles.mapContent}>
                <div style={styles.gridMap}>
                  <svg style={styles.mapSvg} viewBox="0 0 400 300">
                    {/* Grid */}
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

                    {/* Victims */}
                    {victims.map((v, idx) => {
                      const x = 50 + (idx % 4) * 90;
                      const y = 60 + Math.floor(idx / 4) * 80;
                      return (
                        <g key={v.victim_id}>
                          {v.score >= 9 && (
                            <circle cx={x} cy={y} r="20" fill="none" stroke="#ff1744" strokeWidth="2" opacity="0.5">
                              <animate attributeName="r" from="15" to="30" dur="1.5s" repeatCount="indefinite" />
                              <animate attributeName="opacity" from="0.8" to="0" dur="1.5s" repeatCount="indefinite" />
                            </circle>
                          )}
                          <circle
                            cx={x}
                            cy={y}
                            r="12"
                            fill={getSeverityColor(v.score)}
                            stroke="#0a0a0f"
                            strokeWidth="3"
                            style={{ cursor: "pointer" }}
                            onClick={() => setSelectedVictim(v)}
                          />
                          <text x={x} y={y + 4} fill="#0a0a0f" fontSize="10" fontWeight="bold" textAnchor="middle">
                            {v.score}
                          </text>
                          <text x={x} y={y + 28} fill="#8892b0" fontSize="8" textAnchor="middle">
                            {v.victim_id.slice(0, 10)}
                          </text>
                        </g>
                      );
                    })}

                    {/* Rescue Teams */}
                    {rescueTeams.map((t, idx) => {
                      const x = 80 + idx * 90;
                      const y = 240;
                      const assignedVictimIdx = victims.findIndex((v) => v.victim_id === t.assigned_to);
                      return (
                        <g key={t.team_id}>
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
                              <animate attributeName="stroke-dashoffset" from="0" to="-10" dur="0.5s" repeatCount="indefinite" />
                            </line>
                          )}
                          <rect
                            x={x - 15}
                            y={y - 10}
                            width="30"
                            height="20"
                            fill={t.status === "available" ? "#69f0ae" : "#00e5ff"}
                            stroke="#0a0a0f"
                            strokeWidth="2"
                            rx="3"
                            style={{ cursor: "pointer" }}
                            onClick={() => setSelectedTeam(t)}
                          />
                          <text x={x} y={y + 4} fill="#0a0a0f" fontSize="8" fontWeight="bold" textAnchor="middle">
                            {t.team_id.slice(-1)}
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                </div>

                {/* Map Legend */}
                <div style={styles.mapLegend}>
                  <div style={styles.legendItem}>
                    <span style={{ ...styles.legendDot, background: "#ff1744" }} />
                    CRITICAL (9-10)
                  </div>
                  <div style={styles.legendItem}>
                    <span style={{ ...styles.legendDot, background: "#ff9100" }} />
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

            {/* Side Panel */}
            <div style={styles.sidePanel}>
              {selectedVictim && (
                <div style={styles.detailCard}>
                  <div style={styles.detailHeader}>
                    <span>VICTIM DETAILS</span>
                    <button onClick={() => setSelectedVictim(null)} style={styles.closeButton}>✕</button>
                  </div>
                  <div style={styles.detailContent}>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>ID</span>
                      <span style={styles.detailValue}>{selectedVictim.victim_id}</span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>SEVERITY</span>
                      <span style={{...styles.severityBadge, background: getSeverityColor(selectedVictim.score)}}>
                        {selectedVictim.score}/10 - {selectedVictim.priority_level}
                      </span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>PEOPLE</span>
                      <span style={styles.detailValue}>{selectedVictim.num_people}</span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>LOCATION</span>
                      <span style={styles.detailValue}>
                        {selectedVictim.location?.description || 'Unknown'}
                      </span>
                    </div>
                    <div style={styles.descriptionBox}>
                      <span style={styles.detailLabel}>SITUATION</span>
                      <p style={styles.descriptionText}>{selectedVictim.description}</p>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>STATUS</span>
                      <span style={{
                        ...styles.statusBadgeSmall,
                        color: getStatusBadge(selectedVictim.status).text,
                        borderColor: getStatusBadge(selectedVictim.status).border,
                      }}>
                        {selectedVictim.status?.toUpperCase().replace("_", " ")}
                      </span>
                    </div>
                    
                    {/* Quick Actions */}
                    {selectedVictim.status === 'pending' && availableTeams.length > 0 && (
                      <div style={styles.quickActions}>
                        <span style={styles.detailLabel}>ASSIGN TEAM</span>
                        <div style={styles.teamButtons}>
                          {availableTeams.slice(0, 3).map(team => (
                            <button
                              key={team.team_id}
                              onClick={() => handleAssignTeam(team.team_id, selectedVictim.victim_id)}
                              style={styles.assignButton}
                            >
                              {team.team_id}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {selectedTeam && (
                <div style={styles.detailCard}>
                  <div style={styles.detailHeader}>
                    <span>TEAM DETAILS</span>
                    <button onClick={() => setSelectedTeam(null)} style={styles.closeButton}>✕</button>
                  </div>
                  <div style={styles.detailContent}>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>TEAM ID</span>
                      <span style={styles.detailValue}>{selectedTeam.team_id}</span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>NAME</span>
                      <span style={styles.detailValue}>{selectedTeam.name}</span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>STATUS</span>
                      <span style={{
                        ...styles.statusBadgeSmall,
                        color: getStatusBadge(selectedTeam.status).text,
                        borderColor: getStatusBadge(selectedTeam.status).border,
                      }}>
                        {selectedTeam.status?.toUpperCase().replace("_", " ")}
                      </span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>PERSONNEL</span>
                      <span style={styles.detailValue}>{selectedTeam.personnel}</span>
                    </div>
                    {selectedTeam.assigned_to && (
                      <div style={styles.detailRow}>
                        <span style={styles.detailLabel}>ASSIGNED TO</span>
                        <span style={styles.assignedValue}>{selectedTeam.assigned_to}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div style={styles.quickStats}>
                <div style={styles.statBox}>
                  <div style={styles.statValue}>{victims.length}</div>
                  <div style={styles.statLabel}>TOTAL</div>
                </div>
                <div style={styles.statBox}>
                  <div style={{ ...styles.statValue, color: "#ff1744" }}>
                    {victims.filter((v) => v.status === "pending").length}
                  </div>
                  <div style={styles.statLabel}>PENDING</div>
                </div>
                <div style={styles.statBox}>
                  <div style={{ ...styles.statValue, color: "#00e5ff" }}>
                    {victims.filter((v) => v.status === "in_progress").length}
                  </div>
                  <div style={styles.statLabel}>ACTIVE</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "queue" && (
          <div style={styles.queueContainer}>
            <div style={styles.queueHeader}>
              <h2 style={styles.queueTitle}>PRIORITY QUEUE</h2>
              <span style={styles.queueCount}>{victims.length} INCIDENTS</span>
            </div>
            <div style={styles.queueList}>
              {victims
                .sort((a, b) => b.score - a.score)
                .map((victim, index) => (
                  <div
                    key={victim.victim_id}
                    style={{
                      ...styles.queueItem,
                      borderLeftColor: getSeverityColor(victim.score),
                    }}
                    onClick={() => {
                      setSelectedVictim(victim);
                      setActiveTab("map");
                    }}
                  >
                    <div style={styles.queueRank}>#{index + 1}</div>
                    <div style={styles.queueMain}>
                      <div style={styles.queueTop}>
                        <span style={styles.queueId}>{victim.victim_id}</span>
                        <span style={{...styles.queueSeverity, background: getSeverityColor(victim.score)}}>
                          {victim.score}/10
                        </span>
                        <span style={styles.queueLevel}>{victim.priority_level}</span>
                      </div>
                      <div style={styles.queueDesc}>{victim.description}</div>
                      <div style={styles.queueMeta}>
                        <span>📍 {victim.location?.description || 'Unknown'}</span>
                        <span>👥 {victim.num_people} people</span>
                        <span>🕐 {formatTime(victim.timestamp)}</span>
                      </div>
                    </div>
                    <div style={styles.queueStatus}>
                      <span style={{
                        ...styles.statusBadgeSmall,
                        color: getStatusBadge(victim.status).text,
                        borderColor: getStatusBadge(victim.status).border,
                      }}>
                        {victim.status?.toUpperCase().replace("_", " ")}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {activeTab === "teams" && (
          <div style={styles.teamsContainer}>
            <div style={styles.teamsHeader}>
              <h2 style={styles.teamsTitle}>RESCUE TEAMS</h2>
              <div style={styles.teamsStats}>
                <span style={styles.teamStatGreen}>
                  {rescueTeams.filter((t) => t.status === "available").length} AVAILABLE
                </span>
                <span style={styles.teamStatBlue}>
                  {rescueTeams.filter((t) => t.status !== "available").length} DEPLOYED
                </span>
              </div>
            </div>
            <div style={styles.teamsGrid}>
              {rescueTeams.map((team) => (
                <div
                  key={team.team_id}
                  style={{
                    ...styles.teamCard,
                    borderColor: team.status === "available" ? "#69f0ae" : "#00e5ff",
                  }}
                >
                  <div style={styles.teamCardHeader}>
                    <span style={styles.teamId}>{team.team_id}</span>
                    <span style={{...styles.teamStatus, color: getStatusBadge(team.status).text}}>
                      {team.status?.toUpperCase().replace("_", " ")}
                    </span>
                  </div>
                  <div style={styles.teamName}>{team.name}</div>
                  <div style={styles.teamDetails}>
                    <div style={styles.teamDetail}>
                      <span style={styles.teamDetailLabel}>Personnel</span>
                      <span style={styles.teamDetailValue}>{team.personnel}</span>
                    </div>
                    <div style={styles.teamDetail}>
                      <span style={styles.teamDetailLabel}>Vehicle</span>
                      <span style={styles.teamDetailValue}>{team.vehicle}</span>
                    </div>
                  </div>
                  {team.assigned_to && (
                    <div style={styles.teamAssignment}>
                      <div style={styles.assignmentLabel}>ASSIGNED TO</div>
                      <div style={styles.assignmentValue}>{team.assigned_to}</div>
                      {team.eta_minutes !== null && (
                        <div style={styles.etaLabel}>
                          ETA: <span style={styles.etaTime}>
                            {team.eta_minutes === 0 ? "ON SCENE" : `${team.eta_minutes} min`}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                  {!team.assigned_to && (
                    <div style={styles.availableTag}>READY FOR DEPLOYMENT</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "resources" && (
          <div style={styles.resourcesContainer}>
            <div style={styles.resourcesHeader}>
              <h2 style={styles.resourcesTitle}>RESOURCE INVENTORY</h2>
              <span style={styles.lastUpdated}>
                Last updated: {currentTime.toLocaleTimeString()}
              </span>
            </div>
            <div style={styles.resourcesGrid}>
              {Object.entries(inventory).map(([item, data]) => {
                const percentage = data.total > 0 ? (data.available / data.total) * 100 : 0;
                const isLow = percentage < 30;
                const isCritical = percentage < 15;
                return (
                  <div key={item} style={styles.resourceCard}>
                    <div style={styles.resourceHeader}>
                      <span style={styles.resourceName}>
                        {item.replace(/_/g, " ").toUpperCase()}
                      </span>
                      {isCritical && <span style={styles.criticalTag}>LOW!</span>}
                    </div>
                    <div style={styles.resourceBar}>
                      <div
                        style={{
                          ...styles.resourceBarFill,
                          width: `${percentage}%`,
                          background: isCritical ? "#ff1744" : isLow ? "#ff9100" : "#69f0ae",
                        }}
                      />
                    </div>
                    <div style={styles.resourceStats}>
                      <div style={styles.resourceStat}>
                        <span style={styles.resourceStatLabel}>Available</span>
                        <span style={styles.resourceStatValue}>{data.available}</span>
                      </div>
                      <div style={styles.resourceStat}>
                        <span style={styles.resourceStatLabel}>Allocated</span>
                        <span style={styles.resourceStatValueOrange}>{data.allocated}</span>
                      </div>
                      <div style={styles.resourceStat}>
                        <span style={styles.resourceStatLabel}>Total</span>
                        <span style={styles.resourceStatValue}>{data.total}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <div style={styles.footerLeft}>SOLACE AGENT MESH • DISASTER RESPONSE SYSTEM</div>
        <div style={styles.footerCenter}>REST API: {API_BASE_URL}</div>
        <div style={styles.footerRight}>© 2026 Emergency Response Command</div>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%)",
    color: "#e6e6e6",
    fontFamily: "'JetBrains Mono', 'Fira Code', 'SF Mono', monospace",
    position: "relative",
    overflow: "hidden",
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
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 24px",
    borderBottom: "1px solid #1a3a4a",
    background: "rgba(10, 10, 15, 0.95)",
    backdropFilter: "blur(10px)",
  },
  headerLeft: { display: "flex", alignItems: "center", gap: "16px" },
  logoContainer: { display: "flex", alignItems: "center", gap: "12px" },
  logoIcon: { fontSize: "32px", background: "linear-gradient(135deg, #00e5ff, #64ffda)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" },
  title: { fontSize: "20px", fontWeight: 700, color: "#00e5ff", margin: 0, letterSpacing: "2px" },
  subtitle: { fontSize: "10px", color: "#64ffda", margin: 0, letterSpacing: "4px" },
  headerCenter: { display: "flex", gap: "12px" },
  statusIndicators: { display: "flex", gap: "12px", alignItems: "center" },
  criticalBadge: { display: "flex", alignItems: "center", gap: "8px", background: "rgba(255, 23, 68, 0.2)", border: "1px solid #ff1744", padding: "8px 16px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, color: "#ff1744" },
  pulsingDot: { width: "8px", height: "8px", background: "#ff1744", borderRadius: "50%", animation: "pulse 1s infinite" },
  urgentBadge: { background: "rgba(255, 145, 0, 0.2)", border: "1px solid #ff9100", padding: "8px 16px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, color: "#ff9100" },
  teamsBadge: { background: "rgba(0, 229, 255, 0.2)", border: "1px solid #00e5ff", padding: "8px 16px", borderRadius: "4px", fontSize: "12px", fontWeight: 600, color: "#00e5ff" },
  headerRight: { display: "flex", alignItems: "center", gap: "20px" },
  clockContainer: { textAlign: "right" },
  clockLabel: { fontSize: "9px", color: "#64ffda", letterSpacing: "2px" },
  clock: { fontSize: "24px", fontWeight: 700, color: "#00e5ff", fontVariantNumeric: "tabular-nums" },
  dateDisplay: { fontSize: "10px", color: "#8892b0" },
  connectionBadge: { display: "flex", alignItems: "center", gap: "6px", padding: "6px 12px", border: "1px solid", borderRadius: "4px", fontSize: "10px", fontWeight: 600 },
  connectionDot: { width: "6px", height: "6px", borderRadius: "50%" },
  nav: { display: "flex", gap: "4px", padding: "8px 24px", borderBottom: "1px solid #1a3a4a", background: "rgba(13, 17, 23, 0.8)" },
  navButton: { padding: "10px 20px", background: "transparent", border: "1px solid #1a3a4a", borderRadius: "4px", color: "#8892b0", fontSize: "12px", fontWeight: 600, cursor: "pointer", transition: "all 0.2s ease", fontFamily: "inherit", letterSpacing: "1px" },
  navButtonActive: { background: "rgba(0, 229, 255, 0.1)", borderColor: "#00e5ff", color: "#00e5ff" },
  addReportButton: { marginLeft: "auto", padding: "10px 20px", background: "rgba(105, 240, 174, 0.2)", border: "1px solid #69f0ae", borderRadius: "4px", color: "#69f0ae", fontSize: "12px", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
  errorBanner: { background: "rgba(255, 23, 68, 0.2)", borderBottom: "1px solid #ff1744", padding: "8px 24px", color: "#ff1744", fontSize: "12px" },
  main: { padding: "20px 24px", minHeight: "calc(100vh - 200px)" },
  mapLayout: { display: "grid", gridTemplateColumns: "1fr 350px", gap: "20px", height: "calc(100vh - 240px)" },
  mapContainer: { background: "rgba(13, 17, 23, 0.9)", border: "1px solid #1a3a4a", borderRadius: "8px", overflow: "hidden" },
  mapHeader: { display: "flex", justifyContent: "space-between", padding: "12px 16px", borderBottom: "1px solid #1a3a4a", fontSize: "12px", fontWeight: 600, color: "#64ffda", letterSpacing: "1px" },
  mapCoords: { color: "#8892b0" },
  mapContent: { padding: "20px", height: "calc(100% - 50px)", display: "flex", flexDirection: "column" },
  gridMap: { flex: 1, background: "#0a0a0f", borderRadius: "4px", border: "1px solid #1a3a4a", overflow: "hidden" },
  mapSvg: { width: "100%", height: "100%" },
  mapLegend: { display: "flex", gap: "20px", marginTop: "16px", padding: "12px", background: "rgba(26, 58, 74, 0.3)", borderRadius: "4px" },
  legendItem: { display: "flex", alignItems: "center", gap: "8px", fontSize: "10px", color: "#8892b0" },
  legendDot: { width: "12px", height: "12px", borderRadius: "50%" },
  legendSquare: { width: "12px", height: "12px", borderRadius: "2px" },
  sidePanel: { display: "flex", flexDirection: "column", gap: "16px" },
  detailCard: { background: "rgba(13, 17, 23, 0.9)", border: "1px solid #1a3a4a", borderRadius: "8px", overflow: "hidden" },
  detailHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", borderBottom: "1px solid #1a3a4a", fontSize: "11px", fontWeight: 600, color: "#64ffda", letterSpacing: "1px" },
  closeButton: { background: "transparent", border: "none", color: "#8892b0", cursor: "pointer", fontSize: "14px", padding: "4px 8px" },
  detailContent: { padding: "16px" },
  detailRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" },
  detailLabel: { fontSize: "10px", color: "#8892b0", letterSpacing: "1px" },
  detailValue: { fontSize: "12px", color: "#e6e6e6", fontWeight: 500 },
  severityBadge: { padding: "4px 10px", borderRadius: "4px", fontSize: "10px", fontWeight: 700, color: "#0a0a0f" },
  statusBadgeSmall: { padding: "4px 10px", borderRadius: "4px", fontSize: "10px", fontWeight: 600, border: "1px solid", background: "transparent" },
  descriptionBox: { marginTop: "16px", paddingTop: "16px", borderTop: "1px solid #1a3a4a" },
  descriptionText: { fontSize: "12px", color: "#e6e6e6", lineHeight: 1.6, marginTop: "8px" },
  assignedValue: { fontSize: "12px", color: "#00e5ff", fontWeight: 600 },
  quickActions: { marginTop: "16px", paddingTop: "16px", borderTop: "1px solid #1a3a4a" },
  teamButtons: { display: "flex", gap: "8px", marginTop: "8px" },
  assignButton: { padding: "6px 12px", background: "rgba(0, 229, 255, 0.2)", border: "1px solid #00e5ff", borderRadius: "4px", color: "#00e5ff", fontSize: "10px", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
  quickStats: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginTop: "auto" },
  statBox: { background: "rgba(13, 17, 23, 0.9)", border: "1px solid #1a3a4a", borderRadius: "8px", padding: "16px", textAlign: "center" },
  statValue: { fontSize: "28px", fontWeight: 700, color: "#00e5ff" },
  statLabel: { fontSize: "9px", color: "#8892b0", letterSpacing: "1px", marginTop: "4px" },
  queueContainer: { background: "rgba(13, 17, 23, 0.9)", border: "1px solid #1a3a4a", borderRadius: "8px", overflow: "hidden" },
  queueHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderBottom: "1px solid #1a3a4a" },
  queueTitle: { fontSize: "14px", fontWeight: 700, color: "#64ffda", letterSpacing: "2px", margin: 0 },
  queueCount: { fontSize: "12px", color: "#8892b0" },
  queueList: { maxHeight: "calc(100vh - 320px)", overflowY: "auto" },
  queueItem: { display: "flex", alignItems: "flex-start", gap: "16px", padding: "16px 20px", borderBottom: "1px solid #1a3a4a", borderLeft: "4px solid", cursor: "pointer", transition: "background 0.2s ease" },
  queueRank: { fontSize: "18px", fontWeight: 700, color: "#8892b0", minWidth: "40px" },
  queueMain: { flex: 1 },
  queueTop: { display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" },
  queueId: { fontSize: "12px", color: "#00e5ff", fontWeight: 600 },
  queueSeverity: { padding: "2px 8px", borderRadius: "4px", fontSize: "10px", fontWeight: 700, color: "#0a0a0f" },
  queueLevel: { fontSize: "10px", color: "#ff9100", fontWeight: 600, letterSpacing: "1px" },
  queueDesc: { fontSize: "13px", color: "#e6e6e6", marginBottom: "8px", lineHeight: 1.5 },
  queueMeta: { display: "flex", gap: "16px", fontSize: "11px", color: "#8892b0" },
  queueStatus: { display: "flex", alignItems: "flex-start" },
  teamsContainer: { background: "rgba(13, 17, 23, 0.9)", border: "1px solid #1a3a4a", borderRadius: "8px", overflow: "hidden" },
  teamsHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderBottom: "1px solid #1a3a4a" },
  teamsTitle: { fontSize: "14px", fontWeight: 700, color: "#64ffda", letterSpacing: "2px", margin: 0 },
  teamsStats: { display: "flex", gap: "12px" },
  teamStatGreen: { fontSize: "11px", color: "#69f0ae", fontWeight: 600 },
  teamStatBlue: { fontSize: "11px", color: "#00e5ff", fontWeight: 600 },
  teamsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px", padding: "20px" },
  teamCard: { background: "rgba(26, 58, 74, 0.2)", border: "2px solid", borderRadius: "8px", padding: "16px" },
  teamCardHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" },
  teamId: { fontSize: "14px", fontWeight: 700, color: "#00e5ff" },
  teamStatus: { fontSize: "10px", fontWeight: 600, letterSpacing: "1px" },
  teamName: { fontSize: "16px", fontWeight: 600, color: "#e6e6e6", marginBottom: "16px" },
  teamDetails: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "16px" },
  teamDetail: { display: "flex", flexDirection: "column" },
  teamDetailLabel: { fontSize: "9px", color: "#8892b0", letterSpacing: "1px", marginBottom: "4px" },
  teamDetailValue: { fontSize: "12px", color: "#e6e6e6" },
  teamAssignment: { background: "rgba(0, 229, 255, 0.1)", borderRadius: "4px", padding: "12px", marginTop: "8px" },
  assignmentLabel: { fontSize: "9px", color: "#64ffda", letterSpacing: "1px", marginBottom: "4px" },
  assignmentValue: { fontSize: "14px", color: "#00e5ff", fontWeight: 600, marginBottom: "8px" },
  etaLabel: { fontSize: "11px", color: "#8892b0" },
  etaTime: { color: "#ff9100", fontWeight: 600 },
  availableTag: { background: "rgba(105, 240, 174, 0.1)", borderRadius: "4px", padding: "12px", textAlign: "center", fontSize: "11px", color: "#69f0ae", fontWeight: 600, letterSpacing: "1px", marginTop: "8px" },
  resourcesContainer: { background: "rgba(13, 17, 23, 0.9)", border: "1px solid #1a3a4a", borderRadius: "8px", overflow: "hidden" },
  resourcesHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderBottom: "1px solid #1a3a4a" },
  resourcesTitle: { fontSize: "14px", fontWeight: 700, color: "#64ffda", letterSpacing: "2px", margin: 0 },
  lastUpdated: { fontSize: "11px", color: "#8892b0" },
  resourcesGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px", padding: "20px" },
  resourceCard: { background: "rgba(26, 58, 74, 0.2)", border: "1px solid #1a3a4a", borderRadius: "8px", padding: "16px" },
  resourceHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" },
  resourceName: { fontSize: "12px", fontWeight: 600, color: "#e6e6e6", letterSpacing: "1px" },
  criticalTag: { fontSize: "9px", fontWeight: 700, color: "#ff1744", background: "rgba(255, 23, 68, 0.2)", padding: "2px 8px", borderRadius: "4px" },
  resourceBar: { height: "8px", background: "#1a3a4a", borderRadius: "4px", overflow: "hidden", marginBottom: "12px" },
  resourceBarFill: { height: "100%", borderRadius: "4px", transition: "width 0.3s ease" },
  resourceStats: { display: "flex", justifyContent: "space-between" },
  resourceStat: { display: "flex", flexDirection: "column", alignItems: "center" },
  resourceStatLabel: { fontSize: "9px", color: "#8892b0", letterSpacing: "1px", marginBottom: "4px" },
  resourceStatValue: { fontSize: "16px", fontWeight: 700, color: "#69f0ae" },
  resourceStatValueOrange: { fontSize: "16px", fontWeight: 700, color: "#ff9100" },
  footer: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 24px", borderTop: "1px solid #1a3a4a", background: "rgba(10, 10, 15, 0.95)", fontSize: "10px", color: "#8892b0", letterSpacing: "1px" },
  footerLeft: {},
  footerCenter: { color: "#64ffda" },
  footerRight: {},
  // Modal styles
  modalOverlay: { position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2000 },
  modal: { background: "#0d1117", border: "1px solid #1a3a4a", borderRadius: "8px", width: "90%", maxWidth: "500px", maxHeight: "90vh", overflow: "auto" },
  modalHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px", borderBottom: "1px solid #1a3a4a" },
  modalTitle: { fontSize: "14px", fontWeight: 700, color: "#ff1744", margin: 0, letterSpacing: "1px" },
  form: { padding: "20px" },
  formGroup: { marginBottom: "16px" },
  formRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" },
  label: { display: "block", fontSize: "10px", color: "#64ffda", letterSpacing: "1px", marginBottom: "6px" },
  input: { width: "100%", padding: "10px 12px", background: "#1a1a2e", border: "1px solid #1a3a4a", borderRadius: "4px", color: "#e6e6e6", fontSize: "13px", fontFamily: "inherit" },
  textarea: { width: "100%", padding: "10px 12px", background: "#1a1a2e", border: "1px solid #1a3a4a", borderRadius: "4px", color: "#e6e6e6", fontSize: "13px", fontFamily: "inherit", minHeight: "100px", resize: "vertical" },
  formActions: { display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "20px" },
  cancelButton: { padding: "10px 20px", background: "transparent", border: "1px solid #8892b0", borderRadius: "4px", color: "#8892b0", fontSize: "12px", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
  submitButton: { padding: "10px 20px", background: "rgba(255, 23, 68, 0.2)", border: "1px solid #ff1744", borderRadius: "4px", color: "#ff1744", fontSize: "12px", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" },
};

// Add CSS animation
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
`;
document.head.appendChild(styleSheet);