/**
 * Disaster Rescue System - API Integration Module
 * 
 * This module provides integration between the React dashboard
 * and the Solace Agent Mesh REST Gateway endpoints.
 * 
 * REST Gateway Endpoints (from rest_gateway.yaml):
 * - POST /api/victim/report      - Submit victim report
 * - POST /api/victim/priority    - Calculate priority
 * - POST /api/rescue/calculate   - Calculate equipment/personnel
 * - POST /api/rescue/route       - Get route to victim
 * - POST /api/rescue/eta         - Estimate arrival time
 * - GET  /api/resource/inventory - Get inventory status
 * - POST /api/resource/allocate  - Allocate resources
 * - POST /api/resource/release   - Release resources
 * - GET  /api/health            - System health check
 */

// Configuration - Update this to match your deployment
const API_CONFIG = {
  baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:5050',
  webSocketUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8008',
  refreshInterval: 5000, // Poll every 5 seconds
  timeout: 30000,
};

/**
 * Base API client with error handling
 */
class APIClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);
      
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      if (error.name === 'AbortError') {
        throw new APIError('Request timeout', 408);
      }
      throw new APIError(`Network error: ${error.message}`, 0);
    }
  }

  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// Initialize API client
const api = new APIClient(API_CONFIG.baseUrl);

// ============================================================
// VICTIM MANAGEMENT API
// ============================================================

/**
 * Submit a new victim report
 * Endpoint: POST /api/victim/report
 */
export async function submitVictimReport(reportData) {
  const payload = {
    location: reportData.location,
    latitude: reportData.latitude,
    longitude: reportData.longitude,
    description: reportData.description,
    num_people: reportData.numPeople,
    reporter_contact: reportData.reporterContact || null,
  };
  
  return api.post('/api/victim/report', payload);
}

/**
 * Calculate priority for a victim situation
 * Endpoint: POST /api/victim/priority
 */
export async function calculatePriority(victimData) {
  const payload = {
    severity: victimData.severity,
    num_people: victimData.numPeople,
    has_injuries: victimData.hasInjuries,
    additional_factors: {
      fire_hazard: victimData.fireHazard || false,
      flooding: victimData.flooding || false,
      structural_collapse: victimData.structuralCollapse || false,
    },
  };
  
  return api.post('/api/victim/priority', payload);
}

/**
 * Get priority queue of victims
 * Note: This endpoint may need to be added to your REST gateway
 */
export async function getPriorityQueue(limit = 20) {
  try {
    return await api.get('/api/victim/queue', { limit });
  } catch (error) {
    console.warn('Priority queue endpoint not available, using mock data');
    return { victims: [], total: 0 };
  }
}

/**
 * Update victim status
 */
export async function updateVictimStatus(victimId, status) {
  return api.post('/api/victim/status', {
    victim_id: victimId,
    status: status, // 'pending', 'in_progress', 'resolved'
  });
}

// ============================================================
// RESCUE OPERATIONS API
// ============================================================

/**
 * Calculate equipment and personnel needs
 * Endpoint: POST /api/rescue/calculate
 */
export async function calculateRescueNeeds(scenarioData) {
  const payload = {
    scenario_type: scenarioData.scenarioType, // 'building_collapse', 'flood', 'fire', 'medical'
    num_victims: scenarioData.numVictims,
    severity: scenarioData.severity,
    special_conditions: scenarioData.specialConditions || [],
  };
  
  return api.post('/api/rescue/calculate', payload);
}

/**
 * Get route to victim location
 * Endpoint: POST /api/rescue/route
 */
export async function getRoute(origin, destination, options = {}) {
  const payload = {
    origin: {
      lat: origin.lat,
      lng: origin.lng,
    },
    destination: {
      lat: destination.lat,
      lng: destination.lng,
    },
    avoid_hazards: options.avoidHazards || [],
  };
  
  return api.post('/api/rescue/route', payload);
}

/**
 * Estimate arrival time
 * Endpoint: POST /api/rescue/eta
 */
export async function estimateArrival(teamId, victimId) {
  return api.post('/api/rescue/eta', {
    team_id: teamId,
    victim_id: victimId,
  });
}

/**
 * Get all rescue teams status
 * Note: This endpoint may need to be added to your REST gateway
 */
export async function getRescueTeams() {
  try {
    return await api.get('/api/rescue/teams');
  } catch (error) {
    console.warn('Rescue teams endpoint not available');
    return { teams: [] };
  }
}

/**
 * Assign team to victim
 */
export async function assignTeam(teamId, victimId) {
  return api.post('/api/rescue/assign', {
    team_id: teamId,
    victim_id: victimId,
  });
}

// ============================================================
// RESOURCE MANAGEMENT API
// ============================================================

/**
 * Get current inventory status
 * Endpoint: GET /api/resource/inventory
 */
export async function getInventory(itemName = null) {
  if (itemName) {
    return api.get(`/api/resource/inventory/${itemName}`);
  }
  return api.get('/api/resource/inventory');
}

/**
 * Allocate resources to a mission
 * Endpoint: POST /api/resource/allocate
 */
export async function allocateResources(allocationData) {
  const payload = {
    request_id: allocationData.requestId,
    mission_id: allocationData.missionId,
    equipment_list: allocationData.equipmentList.map(item => ({
      item: item.name,
      quantity: item.quantity,
      priority: item.priority || 'MEDIUM',
    })),
  };
  
  return api.post('/api/resource/allocate', payload);
}

/**
 * Release resources from completed mission
 * Endpoint: POST /api/resource/release
 */
export async function releaseResources(missionId) {
  return api.post('/api/resource/release', {
    mission_id: missionId,
  });
}

// ============================================================
// SYSTEM STATUS API
// ============================================================

/**
 * Check system health
 * Endpoint: GET /api/health
 */
export async function checkHealth() {
  return api.get('/api/health');
}

/**
 * Get connection status
 */
export async function getConnectionStatus() {
  try {
    const health = await checkHealth();
    return {
      connected: true,
      status: health.status,
      agents: health.agents || [],
      version: health.version,
    };
  } catch (error) {
    return {
      connected: false,
      status: 'offline',
      error: error.message,
    };
  }
}

// ============================================================
// REAL-TIME UPDATES (WebSocket Integration)
// ============================================================

/**
 * WebSocket connection manager for real-time updates
 */
class WebSocketManager {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.notifyListeners(data.type, data.payload);
          } catch (error) {
            console.error('[WebSocket] Parse error:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected');
          this.scheduleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`[WebSocket] Reconnecting (attempt ${this.reconnectAttempts})...`);
      setTimeout(() => this.connect().catch(() => {}), this.reconnectDelay);
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);

    return () => {
      this.listeners.get(eventType).delete(callback);
    };
  }

  notifyListeners(eventType, payload) {
    const callbacks = this.listeners.get(eventType);
    if (callbacks) {
      callbacks.forEach((callback) => callback(payload));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// WebSocket singleton instance
let wsManager = null;

export function getWebSocketManager() {
  if (!wsManager) {
    wsManager = new WebSocketManager(API_CONFIG.webSocketUrl);
  }
  return wsManager;
}

// ============================================================
// REACT HOOKS FOR DATA FETCHING
// ============================================================

/**
 * Custom hook for fetching victims with auto-refresh
 */
export function useVictims(refreshInterval = API_CONFIG.refreshInterval) {
  const [victims, setVictims] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let mounted = true;

    const fetchVictims = async () => {
      try {
        const data = await getPriorityQueue();
        if (mounted) {
          setVictims(data.victims || []);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchVictims();
    const interval = setInterval(fetchVictims, refreshInterval);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [refreshInterval]);

  return { victims, loading, error, refetch: () => getPriorityQueue() };
}

/**
 * Custom hook for fetching inventory with auto-refresh
 */
export function useInventory(refreshInterval = API_CONFIG.refreshInterval) {
  const [inventory, setInventory] = React.useState({});
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let mounted = true;

    const fetchInventory = async () => {
      try {
        const data = await getInventory();
        if (mounted) {
          setInventory(data.items || data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchInventory();
    const interval = setInterval(fetchInventory, refreshInterval);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [refreshInterval]);

  return { inventory, loading, error, refetch: () => getInventory() };
}

/**
 * Custom hook for connection status
 */
export function useConnectionStatus(checkInterval = 10000) {
  const [status, setStatus] = React.useState({ connected: false, status: 'checking' });

  React.useEffect(() => {
    let mounted = true;

    const checkConnection = async () => {
      const result = await getConnectionStatus();
      if (mounted) {
        setStatus(result);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, checkInterval);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [checkInterval]);

  return status;
}

// Export configuration for external use
export { API_CONFIG, APIError };

// Import React for hooks (ensure React is available)
import React from 'react';
