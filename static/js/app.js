function app() {
    return {
        status: 'disconnected',
        statusText: 'Disconnected',
        isMenuOpen: false,
        activeTab: 'console',
        allLogs: [],
        pending_q: [],
        stats: { rx: 0, tx: 0 },
        sys: {
            cpu: 0,
            ram_p: 0,
            ram_used: 0,
            ram_free: 0,
            ram_total: 0,
            disk_percent: 0,
            disk_used_gb: 0,
            disk_total_gb: 0,
            hostname: '-',
            load_avg: [0, 0, 0],
            cpu_temp: 0,
            client_count: 0,
            clients: []
        },
        gms: {
            latency_ms: 0,
            total_errors: 0,
            rx_types: {},
            tx_types: {},
            last_activity: null
        },
        mysql: {
            status: 'unknown',
            version: '-',
            threads_connected: 0,
            latency_ms: 0,
            error: null,
            qps: 0,
            slow_queries: 0,
            threads_running: 0,
            aborted_connects: 0,
            db_size_mb: 0,
            buffer_pool_usage: 0,
            uptime: 0
        },
        config: {
            gms_ip: '10.80.227.230',
            client_code: 'MEKTEC',
            channel_id: '11111',
            auto_query: true,
            interval_ms: 1000,
            auto_msg_types: 'LocationListMsg,StationListMsg,ContainerListMsg,AreaListMsg,WorkflowListMsg,WorkflowInstanceListMsg'
        },
        manual: {
            msg_type: '',
            body: '{}',
            method: 'socket',
            get isValid() {
                try { JSON.parse(this.body); return true; } catch (e) { return false; }
            }
        },
        countdownText: '0.0s',
        countdown: 0,
        socket: null,

        initws() {
            console.log('Initializing WebSocket...');
            try {
                this.socket = io({
                    path: '/socket.io',
                    transports: ['websocket'],
                    upgrade: true,
                    reconnectionDelay: 2000,
                    reconnectionDelayMax: 10000,
                });
                this.socket.on('connect', async () => {
                    console.log('BFF Ready (Connected)');
                    this.status = 'connected';
                    this.statusText = 'Connected';

                    // Load current config from backend
                    try {
                        const res = await fetch('/api/v1/socket/gms/config');
                        const data = await res.json();
                        if (data.success) {
                            this.config = { ...this.config, ...data.config };
                        }
                    } catch (e) { console.error('Failed to fetch config:', e); }

                    this.saveConfig(); // Sync config with backend
                });
                this.socket.on('connect_error', (err) => console.error('Connection Error:', err));
                this.socket.on('status_update', (data) => {
                    this.status = (data.status || 'disconnected').toLowerCase();
                    this.statusText = data.text;
                });
                this.socket.on('next_query_in', (data) => this.startCountdown(data.duration_ms));
                this.socket.on('log', (data) => {
                    // Map backend (RX/TX/SYS) to frontend display labels
                    let label = data.direction;
                    if (data.direction === 'RX') label = 'RECV';
                    if (data.direction === 'TX') label = 'SENT';

                    this.addLog(label, data.msgType, JSON.stringify(data.payload));
                    this.stats = data.stats;
                });

                this.socket.on('gms:pending', (data) => {
                    this.pending_q = data;
                });

                this.socket.on('health_stats', (data) => {
                    console.log('[HEALTH] Received health_stats data:', data);
                    // Support both wrapped (data.system) and flat formats
                    const s = data.system || data;
                    this.sys = {
                        cpu: s.cpu,
                        ram_p: s.ram_percent || s.ram_p,
                        ram_used: s.ram_used_gb,
                        ram_total: s.ram_total_gb,
                        ram_free: s.ram_free_gb,
                        disk_percent: s.disk_percent,
                        disk_used_gb: s.disk_used_gb,
                        disk_total_gb: s.disk_total_gb,
                        hostname: s.hostname,
                        cpu_temp: s.cpu_temp,
                        client_count: s.client_count,
                        clients: s.clients || []
                    };
                    this.mysql = data.mysql || {};
                    this.gms = data.gms || this.gms;

                    // Log health to console as requested
                    const statsStr = `CPU: ${s.cpu}%, RAM: ${s.ram_p}%, Latency: ${this.gms.latency_ms || 0}ms`;
                    this.addLog('RECV', 'HEALTH_STATS', statsStr);

                    this.updateCharts();

                    // Log after Alpine finishes data binding update
                    this.$nextTick(() => {
                        console.log('[HEALTH] UI successfully updated and displayed health data.');
                    });
                });

                this.socket.on('gms:error', (data) => {
                    console.error('BFF Error:', data);
                    this.addLog('SYSTEM', 'ERROR', `[${data.code}] ${data.message}`);
                });
            } catch (e) {
                console.error('Socket Init Failed:', e);
            }
        },

        addLog(dir, type, payload) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour12: false });
            const payloadStr = typeof payload === 'object' ? JSON.stringify(payload) : payload;

            this.allLogs.unshift({
                time: timeStr,
                direction: dir,
                msgType: type,
                payload: payloadStr
            });

            // Keep last 100 logs
            if (this.allLogs.length > 100) this.allLogs.pop();
        },

        startCountdown(duration) {
            if (this.timer) clearInterval(this.timer);
            let remaining = duration;
            this.timer = setInterval(() => {
                remaining -= 100;
                if (remaining <= 0) {
                    remaining = 0;
                    clearInterval(this.timer);
                }
                this.countdownText = (remaining / 1000).toFixed(1) + 's';
            }, 100);
        },

        async toggleConnection() {
            const action = this.status === 'disconnected' ? 'START' : 'STOP';
            const pwd = prompt(`🚨 ADMIN ACTION REQUIRED 🚨\n\nPlease enter the Admin Password to ${action} the GMS service:`);
            if (pwd === null) return; // Cancelled
            if (pwd.trim() === '') {
                alert('Password cannot be empty.');
                return;
            }

            const endpoint = this.status === 'disconnected' ? '/api/v1/socket/gms/connect' : '/api/v1/socket/gms/disconnect';

            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'X-Admin-Password': pwd }
                });
                const data = await res.json();
                if (!res.ok || !data.success) {
                    alert('❌ Action Failed: ' + (data.detail || data.message || 'Access Denied'));
                } else {
                    // Optional: notify success
                }
            } catch (e) {
                alert('❌ Network error while toggling service.');
            }
        },

        async saveConfig() {
            const res = await fetch('/api/v1/socket/gms/config', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.config)
            });
            const data = await res.json();
            if (data.success) {
                this.addLog('SYSTEM', 'CONFIG', data.message);
            }
        },

        async sendManualRequest() {
            if (!this.manual.msg_type && !this.manual.body.includes('msgType')) return;

            let bodyJson = {};
            let finalMsgType = this.manual.msg_type;

            try {
                bodyJson = JSON.parse(this.manual.body);
                if (bodyJson.msgType) {
                    finalMsgType = bodyJson.msgType;
                }
            } catch (e) {
                if (this.manual.body && this.manual.body !== '{}' && this.manual.body.trim() !== '') {
                    this.addLog('SYSTEM', 'ERROR', 'Invalid JSON Body');
                    return;
                }
            }

            const method = this.manual.method || 'socket';
            const endpoint = method === 'http' ? '/api/v1/socket/gms/send_http' : '/api/v1/socket/gms/send';

            // Log the manual send
            this.addLog('SENT', `${finalMsgType} (${method.toUpperCase()})`, JSON.stringify(bodyJson));
            console.log(`[MANUAL SEND] ${method.toUpperCase()} -> ${finalMsgType}`, bodyJson);

            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ body: { msgType: finalMsgType, ...bodyJson } })
                });
                const data = await res.json();
                console.log(data)
                if (!data.success) {
                    this.addLog('SYSTEM', 'ERROR', data.message);
                    if (data.data) console.error('[GMS ERROR DETAILS]', data.data);
                } else if (method === 'http' && data.data) {
                    // For HTTP, log the direct payload and response from GMS
                    console.log('──────────────────────────────────────────────────');
                    console.log(`🚀 [SENT TO GMS] ${finalMsgType}`);
                    console.log('HEADER:', data.data.request_payload.header);
                    console.log('BODY:', data.data.request_payload.body);
                    console.log('──────────────────────────────────────────────────');
                    console.log('📥 [GMS RESPONSE]', data.data.gms_response);

                    this.addLog('RECV', 'GMS_RESPONSE', JSON.stringify(data.data.gms_response));
                }
            } catch (e) {
                this.addLog('SYSTEM', 'ERROR', 'Request failed: ' + e.message);
            }
        },

        formatJson() {
            try {
                const obj = JSON.parse(this.manual.body);
                this.manual.body = JSON.stringify(obj, null, 4);
            } catch (e) {
                alert('❌ Invalid JSON: ' + e.message);
            }
        },

        // SVG Sparkline (No external library needed)
        history: {
            cpu: Array(30).fill(0),
            ram: Array(30).fill(0),
            latency: Array(30).fill(0),
        },

        initCharts() {
            // No-op: SVG charts are drawn on each update
            this._drawSparkline('cpuChartSvg', this.history.cpu, '#3fb950');
            this._drawSparkline('ramChartSvg', this.history.ram, '#58a6ff');
            this._drawSparkline('gmsLatencyChartSvg', this.history.latency, '#bc8cff', 200);
        },

        updateCharts() {
            this.history.cpu.push(this.sys.cpu);
            this.history.ram.push(this.sys.ram_p);
            this.history.latency.push(this.gms.latency_ms || 0);
            if (this.history.cpu.length > 30) this.history.cpu.shift();
            if (this.history.ram.length > 30) this.history.ram.shift();
            if (this.history.latency.length > 30) this.history.latency.shift();

            this._drawSparkline('cpuChartSvg', this.history.cpu, '#3fb950');
            this._drawSparkline('ramChartSvg', this.history.ram, '#58a6ff');
            this._drawSparkline('gmsLatencyChartSvg', this.history.latency, '#bc8cff', 200);
        },

        _drawSparkline(svgId, values, color, predefinedMax = null) {
            const svg = document.getElementById(svgId);
            if (!svg) return;
            const W = svg.clientWidth || svg.getBoundingClientRect().width || 300;
            const H = svg.clientHeight || svg.getBoundingClientRect().height || 50;

            // Auto-scale max
            let max = predefinedMax || 100;
            if (!predefinedMax) {
                const actualMax = Math.max(...values, 1);
                max = Math.max(actualMax * 1.1, 1);
            }

            const n = values.length;
            if (n < 2) return;

            const stepX = W / (n - 1);
            const getCoords = (v, i) => {
                return { x: i * stepX, y: H - (Math.min(v, max) / max) * (H - 4) - 2 };
            };

            const points = values.map((v, i) => getCoords(v, i));

            // Simple smoothing (Catmull-Rom like)
            let d = `M ${points[0].x},${points[0].y}`;
            for (let i = 0; i < n - 1; i++) {
                const p0 = points[Math.max(i - 1, 0)];
                const p1 = points[i];
                const p2 = points[i + 1];
                const p3 = points[Math.min(i + 2, n - 1)];

                const cp1x = p1.x + (p2.x - p0.x) / 6;
                const cp1y = p1.y + (p2.y - p0.y) / 6;
                const cp2x = p2.x - (p3.x - p1.x) / 6;
                const cp2y = p2.y - (p3.y - p1.y) / 6;

                d += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`;
            }

            const fillPath = `${d} L ${W},${H} L 0,${H} Z`;
            const gradId = `g_${svgId}`;

            svg.innerHTML = `
                        <defs>
                            <linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stop-color="${color}" stop-opacity="0.4"/>
                                <stop offset="100%" stop-color="${color}" stop-opacity="0.0"/>
                            </linearGradient>
                            <filter id="glow_${svgId}">
                                <feGaussianBlur stdDeviation="1.5" result="blur"/>
                                <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                            </filter>
                        </defs>
                        <path d="${fillPath}" fill="url(#${gradId})" style="transition: d 0.3s ease;"/>
                        <path d="${d}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" 
                            style="filter: drop-shadow(0 0 4px ${color}66); transition: d 0.3s ease;"/>
                    `;
        },

        // ─── UI CONFIG EDITOR ──────────────────────────────────────
        cfgData: {
            site: { name: '', shortName: '', primaryColor: '', gmsClientCode: '', logoUrl: '' },
            map: { ENABLE_SOCKET_LOG: false, MULTIPLIER: 0, SNAP_DISTANCE: 0, ANGLE_OFFSET: 0, ORIGIN_OFFSET_X: 0, ORIGIN_OFFSET_Y: 0, DEFAULT_LOC_SIZE: 0, OPACITY: 0 },
            robot: { WIDTH: 0, LENGTH: 0, IDLE_COLOR: '', WORKING_COLOR: '', ERROR_COLOR: '', CHARGING_COLOR: '', OFFLINE_COLOR: '', ID_LABEL_BG: '' },
            colors: {},
            stations: {},
            floors: [],
            containerTypes: []
        },
        cfgPwd: '',
        cfgMsg: '',
        cfgMsgOk: false,

        // Station modal
        showAddStation: false,
        editStationCode: '',
        newStation: { code: '', alias: '', angle: 90, containerType: '', oldCode: '' },

        // Floor modal
        showAddFloor: false,
        editFloorId: null,
        newFloor: { id: '', label: '', image: '', _file: null, _filename: '' },

        // Container type modal
        showAddContainer: false,
        editContainerId: null,
        newContainer: { id: '', name: '', width: '', length: '', color: '#2ecc71', _file: null, _filename: '' },

        // Preview panel state
        activePreviewImg: '',
        activePreviewName: '',
        showPreviewModal: false,
        zoomLevel: 1,

        // Panning state for zoomed images
        pan: { active: false, startX: 0, startY: 0, offX: 0, offY: 0 },

        zoomIn() { this.zoomLevel = Math.min(this.zoomLevel + 0.2, 4); },
        zoomOut() {
            this.zoomLevel = Math.max(this.zoomLevel - 0.2, 0.2);
            if (this.zoomLevel <= 1) this.resetPan();
        },
        resetZoom() {
            this.zoomLevel = 1;
            this.resetPan();
        },

        resetPan() {
            this.pan = { active: false, startX: 0, startY: 0, offX: 0, offY: 0 };
        },

        startPan(e) {
            if (this.zoomLevel <= 1) return;
            this.pan.active = true;
            // Robust coord extraction (clientX can be 0, so check undefined)
            const x = e.clientX !== undefined ? e.clientX : (e.touches ? e.touches[0].clientX : 0);
            const y = e.clientY !== undefined ? e.clientY : (e.touches ? e.touches[0].clientY : 0);
            this.pan.startX = x - this.pan.offX;
            this.pan.startY = y - this.pan.offY;
        },
        doPan(e) {
            if (!this.pan.active) return;
            const x = e.clientX !== undefined ? e.clientX : (e.touches ? e.touches[0].clientX : 0);
            const y = e.clientY !== undefined ? e.clientY : (e.touches ? e.touches[0].clientY : 0);
            this.pan.offX = x - this.pan.startX;
            this.pan.offY = y - this.pan.startY;
        },
        endPan() {
            this.pan.active = false;
        },

        _cfgNotify(msg, ok) {
            this.cfgMsg = msg;
            this.cfgMsgOk = ok;
            setTimeout(() => { this.cfgMsg = ''; }, 4000);
        },

        async checkConfigAccess() {
            const pass = prompt('กรุณากรอกรหัสผ่าน Admin เพื่อเข้าสู่การตั้งค่า:');
            if (!pass) return;

            try {
                const r = await fetch('/api/v1/ui/verify-password', {
                    method: 'POST',
                    headers: { 'X-Admin-Password': pass }
                });
                const d = await r.json();
                if (d.success) {
                    this.cfgPwd = pass;
                    this.activeTab = 'config';
                    this.loadUiConfig();
                } else {
                    alert('❌ รหัสผ่านไม่ถูกต้อง! (Access Denied)');
                }
            } catch (e) {
                alert('❌ เกิดข้อผิดพลาดในการตรวจสอบรหัสผ่าน');
            }
        },

        _cfgHeaders() {
            return { 'X-Admin-Password': this.cfgPwd };
        },

        async loadUiConfig() {
            try {
                const r = await fetch('/api/v1/ui/config');
                const d = await r.json();
                if (d.success) {
                    this.cfgData = d.data;
                    // Set initial preview to first floor
                    if (this.cfgData.floors && this.cfgData.floors.length > 0) {
                        this.activePreviewImg = this.cfgData.floors[0].image;
                        this.activePreviewName = 'Map: ' + this.cfgData.floors[0].label;
                    }
                }
            } catch (e) {
                this._cfgNotify('❌ Failed to load config', false);
            }
        },

        async saveMapConfig() {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            try {
                const r = await fetch('/api/v1/ui/config/map', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(this.cfgData.map)
                });
                const d = await r.json();
                if (d.success) {
                    this._cfgNotify('✅ Global settings saved', true);
                    await this.loadUiConfig();
                } else {
                    this._cfgNotify('❌ ' + (d.detail || d.message), false);
                }
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

        async saveSiteConfig() {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            try {
                const r = await fetch('/api/v1/ui/config/site', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(this.cfgData.site)
                });
                const d = await r.json();
                if (d.success) { this._cfgNotify('✅ Site settings saved', true); await this.loadUiConfig(); }
                else this._cfgNotify('❌ ' + (d.detail || d.message), false);
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

        async saveRobotConfig() {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            try {
                const r = await fetch('/api/v1/ui/config/robot', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(this.cfgData.robot)
                });
                const d = await r.json();
                if (d.success) { this._cfgNotify('✅ Robot settings saved', true); await this.loadUiConfig(); }
                else this._cfgNotify('❌ ' + (d.detail || d.message), false);
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

        async saveColorsConfig() {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            try {
                const r = await fetch('/api/v1/ui/config/colors', {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(this.cfgData.colors)
                });
                const d = await r.json();
                if (d.success) { this._cfgNotify('✅ Colors saved', true); await this.loadUiConfig(); }
                else this._cfgNotify('❌ ' + (d.detail || d.message), false);
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

        async saveStation() {
            const code = this.newStation.code.trim().toUpperCase();
            const alias = this.newStation.alias.trim();

            // --- Client-side Validation ---
            if (!code) return this._cfgNotify('❌ Station Code is required', false);
            if (!alias) return this._cfgNotify('❌ Alias is required', false);
            if (typeof this.newStation.angle !== 'number') return this._cfgNotify('❌ Angle must be a number', false);
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);

            const body = {
                alias,
                angle: this.newStation.angle,
                containerType: this.newStation.containerType
                    ? this.newStation.containerType.split(',').map(s => s.trim()).filter(Boolean)
                    : []
            };

            const isEdit = !!this.editStationCode;
            if (isEdit && code !== this.newStation.oldCode) {
                body.newCode = code;
            }

            const url = isEdit
                ? `/api/v1/ui/config/stations/${this.editStationCode}`
                : `/api/v1/ui/config/stations?code=${code}`;
            const method = isEdit ? 'PATCH' : 'POST';

            try {
                const r = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(body)
                });
                const d = await r.json();
                if (d.success) {
                    this._cfgNotify(`✅ Station ${isEdit ? 'updated' : 'added'}`, true);
                    this.showAddStation = false;
                    this.editStationCode = '';
                    await this.loadUiConfig();
                } else {
                    this._cfgNotify('❌ ' + (d.detail || d.message), false);
                }
            } catch (e) {
                this._cfgNotify('❌ Network error', false);
            }
        },

        async deleteStation(code) {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            if (!confirm(`Delete station '${code}'?`)) return;
            try {
                const r = await fetch(`/api/v1/ui/config/stations/${code}`, {
                    method: 'DELETE',
                    headers: this._cfgHeaders()
                });
                const d = await r.json();
                if (d.success) { this._cfgNotify('✅ Deleted', true); await this.loadUiConfig(); }
                else this._cfgNotify('❌ ' + (d.detail || d.message), false);
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

        async _uploadFile(file, subfolder = '') {
            const fd = new FormData();
            fd.append('file', file);
            const url = `/api/v1/ui/assets/upload${subfolder ? '?subfolder=' + subfolder : ''}`;
            const r = await fetch(url, { method: 'POST', headers: this._cfgHeaders(), body: fd });
            const d = await r.json();
            if (!d.success) throw new Error(d.detail || d.message || 'Upload failed');
            return d.url;
        },

        async saveFloor() {
            if (!this.newFloor.id && this.newFloor.id !== 0) return this._cfgNotify('❌ Floor ID is required', false);
            if (this.newFloor.id < 0 || !Number.isInteger(this.newFloor.id)) return this._cfgNotify('❌ Floor ID must be a positive integer', false);
            if (!this.newFloor.label.trim()) return this._cfgNotify('❌ Label is required', false);
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);

            const isEdit = this.editFloorId !== null;
            if (!isEdit && !this.newFloor._file) return this._cfgNotify('❌ Floor image is required for new floor', false);

            try {
                let imgUrl = this.newFloor.image;
                if (this.newFloor._file) {
                    imgUrl = await this._uploadFile(this.newFloor._file);
                }

                const url = isEdit ? `/api/v1/ui/config/floors/${this.editFloorId}` : '/api/v1/ui/config/floors';
                const method = isEdit ? 'PATCH' : 'POST';

                const body = { id: isEdit ? this.editFloorId : this.newFloor.id, label: this.newFloor.label.trim(), image: imgUrl };
                if (isEdit && this.newFloor.id !== this.editFloorId) {
                    body.newId = this.newFloor.id;
                }

                const r = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(body)
                });
                const d = await r.json();
                if (d.success) {
                    this._cfgNotify(`✅ Floor ${isEdit ? 'updated' : 'added'}`, true);
                    this.showAddFloor = false;
                    this.editFloorId = null;
                    await this.loadUiConfig();
                } else {
                    this._cfgNotify('❌ ' + (d.detail || d.message), false);
                }
            } catch (e) { this._cfgNotify('❌ ' + e.message, false); }
        },

        async deleteFloor(id) {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            if (!confirm(`Delete Floor ${id}?`)) return;
            try {
                const r = await fetch(`/api/v1/ui/config/floors/${id}`, {
                    method: 'DELETE', headers: this._cfgHeaders()
                });
                const d = await r.json();
                if (d.success) { this._cfgNotify('✅ Deleted', true); await this.loadUiConfig(); }
                else this._cfgNotify('❌ ' + (d.detail || d.message), false);
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

        async saveContainerType() {
            if (!this.newContainer.id.trim()) return this._cfgNotify('❌ Type ID is required', false);
            if (!this.newContainer.name.trim()) return this._cfgNotify('❌ Name is required', false);
            if (!this.newContainer.width || this.newContainer.width <= 0) return this._cfgNotify('❌ Width must be > 0', false);
            if (!this.newContainer.length || this.newContainer.length <= 0) return this._cfgNotify('❌ Length must be > 0', false);
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);

            const isEdit = this.editContainerId !== null;
            if (!isEdit && !this.newContainer._file) return this._cfgNotify('❌ Container image is required for new type', false);

            try {
                let imgUrl = this.newContainer.image;
                if (this.newContainer._file) {
                    imgUrl = await this._uploadFile(this.newContainer._file, 'ContainerImg');
                }

                const body = {
                    id: isEdit ? this.editContainerId : this.newContainer.id.trim(),
                    name: this.newContainer.name.trim(),
                    width: parseFloat(this.newContainer.width),
                    length: parseFloat(this.newContainer.length),
                    image: imgUrl,
                    color: this.newContainer.color
                };

                // If editing and ID changed, backend API expects `newType`
                if (isEdit && this.newContainer.id.trim() !== this.editContainerId) {
                    body.newType = this.newContainer.id.trim();
                }

                const url = isEdit ? `/api/v1/ui/config/container-types/${this.editContainerId}` : '/api/v1/ui/config/container-types';
                const method = isEdit ? 'PATCH' : 'POST';

                const r = await fetch(url, {
                    method,
                    headers: { 'Content-Type': 'application/json', ...this._cfgHeaders() },
                    body: JSON.stringify(body)
                });
                const d = await r.json();
                if (d.success) {
                    this._cfgNotify(`✅ Container type ${isEdit ? 'updated' : 'added'}`, true);
                    this.showAddContainer = false;
                    this.editContainerId = null;
                    await this.loadUiConfig();
                } else {
                    this._cfgNotify('❌ ' + (d.detail || d.message), false);
                }
            } catch (e) { this._cfgNotify('❌ ' + e.message, false); }
        },

        async deleteContainerType(id) {
            if (!this.cfgPwd) return this._cfgNotify('❌ Password required', false);
            if (!confirm(`Delete container type '${id}'?`)) return;
            try {
                const r = await fetch(`/api/v1/ui/config/container-types/${id}`, {
                    method: 'DELETE', headers: this._cfgHeaders()
                });
                const d = await r.json();
                if (d.success) { this._cfgNotify('✅ Deleted', true); await this.loadUiConfig(); }
                else this._cfgNotify('❌ ' + (d.detail || d.message), false);
            } catch (e) { this._cfgNotify('❌ Network error', false); }
        },

    }
}

