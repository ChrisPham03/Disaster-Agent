import React, { useState, useEffect, useCallback } from "react";

// Mock data for demonstration - in production, this comes from your REST API
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
  {
    victim_id: "V-6c5f4e3d",
    score: 5,
    priority_level: "SERIOUS",
    location: { lat: 13.7280, lng: 100.5245, description: "Silom Road, Bangkok" },
    description: "Flood victims, 8 people stranded on rooftop",
    num_people: 8,
    status: "pending",
    color_code: "orange",
    timestamp: new Date(Date.now() - 900000).toISOString(),
  },
  {
    victim_id: "V-5d6g5f4e",
    score: 3,
    priority_level: "MINOR",
    location: { lat: 13.7650, lng: 100.5380, description: "Chatuchak Market" },
    description: "Minor injuries from crowd crush, anxiety",
    num_people: 3,
    status: "pending",
    color_code: "yellow",
    timestamp: new Date(Date.now() - 1200000).toISOString(),
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
    status: "on_scene",
    assigned_to: "V-7b4e3d2c",
    eta_minutes: 0,
    personnel: 4,
    vehicle: "Ambulance Unit",
  },
  {
    team_id: "T-Charlie",
    name: "Charlie SAR Team",
    location: { lat: 13.7400, lng: 100.5200 },
    status: "available",
    assigned_to: null,
    eta_minutes: null,
    personnel: 8,
    vehicle: "Rescue Boat + Truck",
  },
];

const MOCK_INVENTORY = {
  stretcher: { total: 15, available: 10, allocated: 5 },
  first_aid_kit: { total: 50, available: 42, allocated: 8 },
  hydraulic_cutter: { total: 4, available: 2, allocated: 2 },
  oxygen_tank: { total: 20, available: 15, allocated: 5 },
  defibrillator: { total: 6, available: 4, allocated: 2 },
  life_vest: { total: 30, available: 22, allocated: 8 },
  thermal_blanket: { total: 100, available: 85, allocated: 15 },
};

// API configuration - adjust to match your REST gateway
const API_BASE_URL = "http://localhost:5050";

export default function DisasterRescueDashboard() {
  const [victims, setVictims] = useState(MOCK_VICTIMS);
  const [rescueTeams, setRescueTeams] = useState(MOCK_RESCUE_TEAMS);
  const [inventory, setInventory] = useState(MOCK_INVENTORY);
  const [selectedVictim, setSelectedVictim] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [connectionStatus, setConnectionStatus] = useState("demo");
  const [activeTab, setActiveTab] = useState("map");

  // Update clock every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Simulated API fetch - replace with real API calls
  const fetchData = useCallback(async () => {
    try {
      // In production, uncomment these:
      // const victimsRes = await fetch(`${API_BASE_URL}/api/victim/queue`);
      // const teamsRes = await fetch(`${API_BASE_URL}/api/rescue/teams`);
      // const inventoryRes = await fetch(`${API_BASE_URL}/api/resource/inventory`);
      setConnectionStatus("demo");
    } catch (error) {
      console.error("API fetch error:", error);
      setConnectionStatus("offline");
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

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
    const date = new Date(isoString);
    const mins = Math.floor((Date.now() - date) / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m ago`;
  };

  const criticalCount = victims.filter((v) => v.score >= 9).length;
  const urgentCount = victims.filter((v) => v.score >= 7 && v.score < 9).length;
  const activeTeams = rescueTeams.filter((t) => t.status !== "available").length;

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
              borderColor: connectionStatus === "demo" ? "#ff9100" : "#ff1744",
            }}
          >
            <span
              style={{
                ...styles.connectionDot,
                background: connectionStatus === "demo" ? "#ff9100" : "#ff1744",
              }}
            />
            {connectionStatus.toUpperCase()} MODE
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
      </nav>

      {/* Main Content */}
      <main style={styles.main}>
        {activeTab === "map" && (
          <div style={styles.mapLayout}>
            {/* Map Panel */}
            <div style={styles.mapContainer}>
              <div style={styles.mapHeader}>
                <span>LIVE SITUATION MAP</span>
                <span style={styles.mapCoords}>BANGKOK METROPOLITAN AREA</span>
              </div>
              <div style={styles.mapContent}>
                {/* ASCII-style map visualization */}
                <div style={styles.gridMap}>
                  {/* Grid lines */}
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
                      const x = 50 + idx * 80;
                      const y = 80 + (idx % 2) * 100;
                      return (
                        <g key={v.victim_id}>
                          {/* Pulse ring for critical */}
                          {v.score >= 9 && (
                            <circle
                              cx={x}
                              cy={y}
                              r="20"
                              fill="none"
                              stroke="#ff1744"
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

                    {/* Rescue Teams */}
                    {rescueTeams.map((t, idx) => {
                      const x = 100 + idx * 100;
                      const y = 200;
                      return (
                        <g key={t.team_id}>
                          {/* Direction line to assigned victim */}
                          {t.assigned_to && (
                            <line
                              x1={x}
                              y1={y}
                              x2={50 + victims.findIndex((v) => v.victim_id === t.assigned_to) * 80}
                              y2={80 + (victims.findIndex((v) => v.victim_id === t.assigned_to) % 2) * 100}
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
                          <text
                            x={x}
                            y={y + 4}
                            fill="#0a0a0f"
                            fontSize="8"
                            fontWeight="bold"
                            textAnchor="middle"
                          >
                            {t.team_id.slice(2, 3)}
                          </text>
                          <text
                            x={x}
                            y={y + 32}
                            fill="#64ffda"
                            fontSize="8"
                            textAnchor="middle"
                          >
                            {t.name.split(" ")[0]}
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
                    <span style={{ ...styles.legendDot, background: "#ffea00" }} />
                    SERIOUS (5-6)
                  </div>
                  <div style={styles.legendItem}>
                    <span style={{ ...styles.legendSquare, background: "#00e5ff" }} />
                    TEAM ACTIVE
                  </div>
                  <div style={styles.legendItem}>
                    <span style={{ ...styles.legendSquare, background: "#69f0ae" }} />
                    TEAM AVAILABLE
                  </div>
                </div>
              </div>
            </div>

            {/* Side Panel */}
            <div style={styles.sidePanel}>
              {/* Selected Victim Details */}
              {selectedVictim && (
                <div style={styles.detailCard}>
                  <div style={styles.detailHeader}>
                    <span>VICTIM DETAILS</span>
                    <button
                      onClick={() => setSelectedVictim(null)}
                      style={styles.closeButton}
                    >
                      ✕
                    </button>
                  </div>
                  <div style={styles.detailContent}>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>ID</span>
                      <span style={styles.detailValue}>{selectedVictim.victim_id}</span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>SEVERITY</span>
                      <span
                        style={{
                          ...styles.severityBadge,
                          background: getSeverityColor(selectedVictim.score),
                        }}
                      >
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
                        {selectedVictim.location.description}
                      </span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>COORDS</span>
                      <span style={styles.coordsValue}>
                        {selectedVictim.location.lat.toFixed(4)}, {selectedVictim.location.lng.toFixed(4)}
                      </span>
                    </div>
                    <div style={styles.descriptionBox}>
                      <span style={styles.detailLabel}>SITUATION</span>
                      <p style={styles.descriptionText}>{selectedVictim.description}</p>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>STATUS</span>
                      <span
                        style={{
                          ...styles.statusBadgeSmall,
                          ...getStatusBadge(selectedVictim.status),
                          color: getStatusBadge(selectedVictim.status).text,
                          borderColor: getStatusBadge(selectedVictim.status).border,
                        }}
                      >
                        {selectedVictim.status.toUpperCase().replace("_", " ")}
                      </span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>REPORTED</span>
                      <span style={styles.detailValue}>
                        {formatTime(selectedVictim.timestamp)}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Selected Team Details */}
              {selectedTeam && (
                <div style={styles.detailCard}>
                  <div style={styles.detailHeader}>
                    <span>TEAM DETAILS</span>
                    <button
                      onClick={() => setSelectedTeam(null)}
                      style={styles.closeButton}
                    >
                      ✕
                    </button>
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
                      <span
                        style={{
                          ...styles.statusBadgeSmall,
                          color: getStatusBadge(selectedTeam.status).text,
                          borderColor: getStatusBadge(selectedTeam.status).border,
                        }}
                      >
                        {selectedTeam.status.toUpperCase().replace("_", " ")}
                      </span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>PERSONNEL</span>
                      <span style={styles.detailValue}>{selectedTeam.personnel}</span>
                    </div>
                    <div style={styles.detailRow}>
                      <span style={styles.detailLabel}>VEHICLE</span>
                      <span style={styles.detailValue}>{selectedTeam.vehicle}</span>
                    </div>
                    {selectedTeam.assigned_to && (
                      <>
                        <div style={styles.detailRow}>
                          <span style={styles.detailLabel}>ASSIGNED TO</span>
                          <span style={styles.assignedValue}>
                            {selectedTeam.assigned_to}
                          </span>
                        </div>
                        <div style={styles.detailRow}>
                          <span style={styles.detailLabel}>ETA</span>
                          <span style={styles.etaValue}>
                            {selectedTeam.eta_minutes === 0
                              ? "ON SCENE"
                              : `${selectedTeam.eta_minutes} MIN`}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div style={styles.quickStats}>
                <div style={styles.statBox}>
                  <div style={styles.statValue}>{victims.length}</div>
                  <div style={styles.statLabel}>TOTAL INCIDENTS</div>
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
                  <div style={styles.statLabel}>IN PROGRESS</div>
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
                        <span
                          style={{
                            ...styles.queueSeverity,
                            background: getSeverityColor(victim.score),
                          }}
                        >
                          {victim.score}/10
                        </span>
                        <span style={styles.queueLevel}>{victim.priority_level}</span>
                      </div>
                      <div style={styles.queueDesc}>{victim.description}</div>
                      <div style={styles.queueMeta}>
                        <span>📍 {victim.location.description}</span>
                        <span>👥 {victim.num_people} people</span>
                        <span>🕐 {formatTime(victim.timestamp)}</span>
                      </div>
                    </div>
                    <div style={styles.queueStatus}>
                      <span
                        style={{
                          ...styles.statusBadgeSmall,
                          color: getStatusBadge(victim.status).text,
                          borderColor: getStatusBadge(victim.status).border,
                        }}
                      >
                        {victim.status.toUpperCase().replace("_", " ")}
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
                    borderColor:
                      team.status === "available"
                        ? "#69f0ae"
                        : team.status === "en_route"
                        ? "#ff9100"
                        : "#00e5ff",
                  }}
                >
                  <div style={styles.teamCardHeader}>
                    <span style={styles.teamId}>{team.team_id}</span>
                    <span
                      style={{
                        ...styles.teamStatus,
                        color: getStatusBadge(team.status).text,
                      }}
                    >
                      {team.status.toUpperCase().replace("_", " ")}
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
                      <div style={styles.etaLabel}>
                        ETA:{" "}
                        <span style={styles.etaTime}>
                          {team.eta_minutes === 0 ? "ON SCENE" : `${team.eta_minutes} min`}
                        </span>
                      </div>
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
                const percentage = (data.available / data.total) * 100;
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
                          background: isCritical
                            ? "#ff1744"
                            : isLow
                            ? "#ff9100"
                            : "#69f0ae",
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
                        <span style={styles.resourceStatValueOrange}>
                          {data.allocated}
                        </span>
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
        <div style={styles.footerLeft}>
          SOLACE AGENT MESH • DISASTER RESPONSE SYSTEM
        </div>
        <div style={styles.footerCenter}>
          REST API: {API_BASE_URL}
        </div>
        <div style={styles.footerRight}>
          © 2026 Emergency Response Command
        </div>
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
    background:
      "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,229,255,0.03) 2px, rgba(0,229,255,0.03) 4px)",
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
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  },
  logoContainer: {
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
  },
  statusIndicators: {
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
    animation: "pulse 2s infinite",
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
    fontVariantNumeric: "tabular-nums",
  },
  dateDisplay: {
    fontSize: "10px",
    color: "#8892b0",
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
  nav: {
    display: "flex",
    gap: "4px",
    padding: "8px 24px",
    borderBottom: "1px solid #1a3a4a",
    background: "rgba(13, 17, 23, 0.8)",
  },
  navButton: {
    padding: "10px 20px",
    background: "transparent",
    border: "1px solid #1a3a4a",
    borderRadius: "4px",
    color: "#8892b0",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.2s ease",
    fontFamily: "inherit",
    letterSpacing: "1px",
  },
  navButtonActive: {
    background: "rgba(0, 229, 255, 0.1)",
    borderColor: "#00e5ff",
    color: "#00e5ff",
  },
  main: {
    padding: "20px 24px",
    minHeight: "calc(100vh - 200px)",
  },
  mapLayout: {
    display: "grid",
    gridTemplateColumns: "1fr 350px",
    gap: "20px",
    height: "calc(100vh - 240px)",
  },
  mapContainer: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
  },
  mapHeader: {
    display: "flex",
    justifyContent: "space-between",
    padding: "12px 16px",
    borderBottom: "1px solid #1a3a4a",
    fontSize: "12px",
    fontWeight: 600,
    color: "#64ffda",
    letterSpacing: "1px",
  },
  mapCoords: {
    color: "#8892b0",
  },
  mapContent: {
    padding: "20px",
    height: "calc(100% - 50px)",
    display: "flex",
    flexDirection: "column",
  },
  gridMap: {
    flex: 1,
    background: "#0a0a0f",
    borderRadius: "4px",
    border: "1px solid #1a3a4a",
    overflow: "hidden",
  },
  mapSvg: {
    width: "100%",
    height: "100%",
  },
  mapLegend: {
    display: "flex",
    gap: "20px",
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
  legendDot: {
    width: "12px",
    height: "12px",
    borderRadius: "50%",
  },
  legendSquare: {
    width: "12px",
    height: "12px",
    borderRadius: "2px",
  },
  sidePanel: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  detailCard: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
  },
  detailHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    borderBottom: "1px solid #1a3a4a",
    fontSize: "11px",
    fontWeight: 600,
    color: "#64ffda",
    letterSpacing: "1px",
  },
  closeButton: {
    background: "transparent",
    border: "none",
    color: "#8892b0",
    cursor: "pointer",
    fontSize: "14px",
    padding: "4px 8px",
  },
  detailContent: {
    padding: "16px",
  },
  detailRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "12px",
  },
  detailLabel: {
    fontSize: "10px",
    color: "#8892b0",
    letterSpacing: "1px",
  },
  detailValue: {
    fontSize: "12px",
    color: "#e6e6e6",
    fontWeight: 500,
  },
  coordsValue: {
    fontSize: "11px",
    color: "#64ffda",
    fontFamily: "'JetBrains Mono', monospace",
  },
  severityBadge: {
    padding: "4px 10px",
    borderRadius: "4px",
    fontSize: "10px",
    fontWeight: 700,
    color: "#0a0a0f",
  },
  statusBadgeSmall: {
    padding: "4px 10px",
    borderRadius: "4px",
    fontSize: "10px",
    fontWeight: 600,
    border: "1px solid",
    background: "transparent",
  },
  descriptionBox: {
    marginTop: "16px",
    paddingTop: "16px",
    borderTop: "1px solid #1a3a4a",
  },
  descriptionText: {
    fontSize: "12px",
    color: "#e6e6e6",
    lineHeight: 1.6,
    marginTop: "8px",
  },
  assignedValue: {
    fontSize: "12px",
    color: "#00e5ff",
    fontWeight: 600,
  },
  etaValue: {
    fontSize: "14px",
    color: "#ff9100",
    fontWeight: 700,
  },
  quickStats: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "12px",
    marginTop: "auto",
  },
  statBox: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    padding: "16px",
    textAlign: "center",
  },
  statValue: {
    fontSize: "28px",
    fontWeight: 700,
    color: "#00e5ff",
  },
  statLabel: {
    fontSize: "9px",
    color: "#8892b0",
    letterSpacing: "1px",
    marginTop: "4px",
  },
  queueContainer: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
  },
  queueHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 20px",
    borderBottom: "1px solid #1a3a4a",
  },
  queueTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#64ffda",
    letterSpacing: "2px",
    margin: 0,
  },
  queueCount: {
    fontSize: "12px",
    color: "#8892b0",
  },
  queueList: {
    maxHeight: "calc(100vh - 320px)",
    overflowY: "auto",
  },
  queueItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: "16px",
    padding: "16px 20px",
    borderBottom: "1px solid #1a3a4a",
    borderLeft: "4px solid",
    cursor: "pointer",
    transition: "background 0.2s ease",
  },
  queueRank: {
    fontSize: "18px",
    fontWeight: 700,
    color: "#8892b0",
    minWidth: "40px",
  },
  queueMain: {
    flex: 1,
  },
  queueTop: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginBottom: "8px",
  },
  queueId: {
    fontSize: "12px",
    color: "#00e5ff",
    fontWeight: 600,
  },
  queueSeverity: {
    padding: "2px 8px",
    borderRadius: "4px",
    fontSize: "10px",
    fontWeight: 700,
    color: "#0a0a0f",
  },
  queueLevel: {
    fontSize: "10px",
    color: "#ff9100",
    fontWeight: 600,
    letterSpacing: "1px",
  },
  queueDesc: {
    fontSize: "13px",
    color: "#e6e6e6",
    marginBottom: "8px",
    lineHeight: 1.5,
  },
  queueMeta: {
    display: "flex",
    gap: "16px",
    fontSize: "11px",
    color: "#8892b0",
  },
  queueStatus: {
    display: "flex",
    alignItems: "flex-start",
  },
  teamsContainer: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
  },
  teamsHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 20px",
    borderBottom: "1px solid #1a3a4a",
  },
  teamsTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#64ffda",
    letterSpacing: "2px",
    margin: 0,
  },
  teamsStats: {
    display: "flex",
    gap: "12px",
  },
  teamStatGreen: {
    fontSize: "11px",
    color: "#69f0ae",
    fontWeight: 600,
  },
  teamStatBlue: {
    fontSize: "11px",
    color: "#00e5ff",
    fontWeight: 600,
  },
  teamsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
    gap: "16px",
    padding: "20px",
  },
  teamCard: {
    background: "rgba(26, 58, 74, 0.2)",
    border: "2px solid",
    borderRadius: "8px",
    padding: "16px",
  },
  teamCardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },
  teamId: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#00e5ff",
  },
  teamStatus: {
    fontSize: "10px",
    fontWeight: 600,
    letterSpacing: "1px",
  },
  teamName: {
    fontSize: "16px",
    fontWeight: 600,
    color: "#e6e6e6",
    marginBottom: "16px",
  },
  teamDetails: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
    marginBottom: "16px",
  },
  teamDetail: {
    display: "flex",
    flexDirection: "column",
  },
  teamDetailLabel: {
    fontSize: "9px",
    color: "#8892b0",
    letterSpacing: "1px",
    marginBottom: "4px",
  },
  teamDetailValue: {
    fontSize: "12px",
    color: "#e6e6e6",
  },
  teamAssignment: {
    background: "rgba(0, 229, 255, 0.1)",
    borderRadius: "4px",
    padding: "12px",
    marginTop: "8px",
  },
  assignmentLabel: {
    fontSize: "9px",
    color: "#64ffda",
    letterSpacing: "1px",
    marginBottom: "4px",
  },
  assignmentValue: {
    fontSize: "14px",
    color: "#00e5ff",
    fontWeight: 600,
    marginBottom: "8px",
  },
  etaLabel: {
    fontSize: "11px",
    color: "#8892b0",
  },
  etaTime: {
    color: "#ff9100",
    fontWeight: 600,
  },
  availableTag: {
    background: "rgba(105, 240, 174, 0.1)",
    borderRadius: "4px",
    padding: "12px",
    textAlign: "center",
    fontSize: "11px",
    color: "#69f0ae",
    fontWeight: 600,
    letterSpacing: "1px",
    marginTop: "8px",
  },
  resourcesContainer: {
    background: "rgba(13, 17, 23, 0.9)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    overflow: "hidden",
  },
  resourcesHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 20px",
    borderBottom: "1px solid #1a3a4a",
  },
  resourcesTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#64ffda",
    letterSpacing: "2px",
    margin: 0,
  },
  lastUpdated: {
    fontSize: "11px",
    color: "#8892b0",
  },
  resourcesGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "16px",
    padding: "20px",
  },
  resourceCard: {
    background: "rgba(26, 58, 74, 0.2)",
    border: "1px solid #1a3a4a",
    borderRadius: "8px",
    padding: "16px",
  },
  resourceHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "12px",
  },
  resourceName: {
    fontSize: "12px",
    fontWeight: 600,
    color: "#e6e6e6",
    letterSpacing: "1px",
  },
  criticalTag: {
    fontSize: "9px",
    fontWeight: 700,
    color: "#ff1744",
    background: "rgba(255, 23, 68, 0.2)",
    padding: "2px 8px",
    borderRadius: "4px",
    animation: "pulse 1s infinite",
  },
  resourceBar: {
    height: "8px",
    background: "#1a3a4a",
    borderRadius: "4px",
    overflow: "hidden",
    marginBottom: "12px",
  },
  resourceBarFill: {
    height: "100%",
    borderRadius: "4px",
    transition: "width 0.3s ease",
  },
  resourceStats: {
    display: "flex",
    justifyContent: "space-between",
  },
  resourceStat: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  resourceStatLabel: {
    fontSize: "9px",
    color: "#8892b0",
    letterSpacing: "1px",
    marginBottom: "4px",
  },
  resourceStatValue: {
    fontSize: "16px",
    fontWeight: 700,
    color: "#69f0ae",
  },
  resourceStatValueOrange: {
    fontSize: "16px",
    fontWeight: 700,
    color: "#ff9100",
  },
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
  footerLeft: {},
  footerCenter: {
    color: "#64ffda",
  },
  footerRight: {},
};

// Add keyframes for animations
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
`;
document.head.appendChild(styleSheet);
