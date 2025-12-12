import socket
import threading
import time
import pygame
import subprocess
import platform
import logging
import json
import traceback

class NetworkManager:
    def __init__(self):
        self.is_host = False
        self.connected = False
        self.socket = None
        self.client_socket = None
        self.host_address = ""
        self.port = 7777  # ✅ Pastikan ini sama di host dan client
        self.error_message = ""
        self.status_message = "Not connected"
        self.zerotier_ip = self.get_zerotier_ip()

    logging.basicConfig(
        filename='network_debug.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s'
    )
        
    def get_zerotier_ip(self):
        """Get ZeroTier Managed IP - VERSION FOR .EXE dengan fallback"""
        try:
            # Coba dengan psutil terlebih dahulu
            import socket
            import psutil
            
            # Cari interface yang memiliki IP dari range ZeroTier (192.168.191.x)
            for interface, addrs in psutil.net_if_addrs().items():
                # Cek apakah interface mengandung 'ZeroTier' atau 'zt'
                if 'zerotier' in interface.lower() or 'zt' in interface.lower():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:  # IPv4
                            ip = addr.address
                            # Filter IP ZeroTier (biasanya 192.168.191.x)
                            if ip.startswith('192.168.191.'):
                                return ip
                            elif ip.startswith('10.'):
                                # Bisa juga 10.x.x.x untuk ZeroTier
                                return ip
            
            # Jika tidak ditemukan dengan nama interface, cari berdasarkan range IP
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        # ZeroTier range umum
                        if ip.startswith('192.168.191.'):
                            return ip
                        elif ip.startswith('10.'):
                            # Cek apakah ini IP private (bukan localhost)
                            if not ip.startswith('10.0.0.') and not ip.startswith('10.1.10.'):
                                return ip
                            
        except ImportError:
            # Jika psutil tidak tersedia di .exe, coba method alternatif
            print("⚠️ psutil not available, using alternative method")
            return self.get_zerotier_ip_alternative()
        except Exception as e:
            print(f"⚠️ Error with psutil: {e}, using alternative method")
            return self.get_zerotier_ip_alternative()
        
        return "IP_NOT_FOUND"
    
    def get_zerotier_ip_alternative(self):
        """Alternatif jika psutil tidak tersedia - untuk .exe"""
        try:
            import socket
            import subprocess
            import platform
            import re
            
            system = platform.system()
            
            if system == "Windows":
                # Gunakan ipconfig di Windows
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                output = result.stdout
                
                # Parse output untuk cari ZeroTier IP
                # Cari pattern: IPv4 Address. . . . . . . . . . . : 192.168.191.x
                pattern = r'IPv4 Address[ .:]+(192\.168\.191\.\d+)'
                matches = re.findall(pattern, output)
                
                if matches:
                    return matches[0]
                
                # Cari pattern untuk adapter ZeroTier
                lines = output.split('\n')
                found_zerotier = False
                for line in lines:
                    if 'zerotier' in line.lower() or 'zt' in line.lower():
                        found_zerotier = True
                        continue
                    
                    if found_zerotier and 'IPv4 Address' in line:
                        # Contoh: IPv4 Address. . . . . . . . . . . : 192.168.191.100
                        parts = line.split(':')
                        if len(parts) > 1:
                            ip = parts[1].strip()
                            if self.is_valid_ip(ip):
                                return ip
                
                # Coba dapatkan semua IP lokal
                hostname = socket.gethostname()
                local_ips = socket.gethostbyname_ex(hostname)[2]
                
                for ip in local_ips:
                    if ip.startswith('192.168.191.'):
                        return ip
                    elif ip.startswith('10.'):
                        # Cek jika bukan localhost
                        if ip != '127.0.0.1' and not ip.startswith('10.0.0.'):
                            return ip
            
            else:
                # Untuk Linux/Mac, gunakan ifconfig atau ip
                try:
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                    output = result.stdout
                    
                    # Cari IP ZeroTier
                    pattern = r'inet (192\.168\.191\.\d+)'
                    matches = re.findall(pattern, output)
                    
                    if matches:
                        return matches[0]
                except:
                    pass
            
            return "IP_NOT_FOUND"
            
        except Exception as e:
            print(f"Error in alternative IP detection: {e}")
            return "ERROR"
    
    def is_valid_ip(self, ip):
        """Check if string is a valid IP address"""
        import re
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        return False
        
    def refresh_zerotier_ip(self):
        """Refresh ZeroTier IP (call when in host page)"""
        old_ip = self.zerotier_ip
        self.zerotier_ip = self.get_zerotier_ip()
        
        # Log perubahan
        if old_ip != self.zerotier_ip:
            logging.info(f"ZeroTier IP refreshed: {old_ip} -> {self.zerotier_ip}")
        
        return self.zerotier_ip
    
    def start_host(self):
        """Start as host/server"""
        try:
            self.is_host = True
            self.connected = False
            self.error_message = ""
            self.status_message = "Starting host..."
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # === TAMBAHKAN INI ===
            # Set socket options untuk firewall traversal
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # No delay
            if hasattr(socket, 'SO_KEEPALIVE'):
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(1)
            self.socket.settimeout(0.5)  # Non-blocking accept
            
            self.status_message = "Host started - Waiting for connection..."
            return True
            
        except Exception as e:
            self.error_message = f"Error starting host: {str(e)}"
            return False

    def update_host(self):
        """Update host state - check for incoming connections"""
        if self.is_host and not self.connected:
            try:
                self.client_socket, addr = self.socket.accept()
                self.connected = True
                self.status_message = f"Player connected: {addr[0]}"
                
                # PERBAIKAN: Set socket ke non-blocking untuk game
                self.client_socket.setblocking(False)
                
                # PERBAIKAN: Juga update error_message agar kosong
                self.error_message = ""
                
                # Log connection
                print(f"✅ Host: Player connected from {addr[0]}")
                logging.info(f"Host: Player connected from {addr[0]}")
                
                return True
            except socket.timeout:
                pass  # No connection yet
            except Exception as e:
                self.error_message = f"Connection error: {str(e)}"
                logging.error(f"Host connection error: {e}")
        return False
    
    def connect_to_host(self, host_ip):
        """Connect to host as client - DENGAN LOGGING LEBIH BAIK"""
        import socket
        import time
        
        logging.info(f"🔗 CONNECTING to {host_ip}:{self.port}")
        print(f"🔗 Client: Attempting to connect to {host_ip}:{self.port}")
        
        # Clear previous state
        self.connected = False
        self.error_message = ""
        self.status_message = f"Connecting to {host_ip}..."
        
        # Validate IP
        if not self._validate_ip(host_ip):
            self.error_message = f"Invalid IP address: {host_ip}"
            logging.error(f"❌ Invalid IP: {host_ip}")
            return False
        
        max_retries = 2
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Create new socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # Set timeout berdasarkan attempt
                timeout = 5 if attempt == 0 else 5
                sock.settimeout(timeout)
                
                logging.info(f"Attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)")
                print(f"🔄 Attempt {attempt + 1} (timeout: {timeout}s)...")
                
                # Try connect
                start_time = time.time()
                sock.connect((host_ip, self.port))
                connect_time = time.time() - start_time
                
                # Success!
                self.socket = sock
                self.connected = True
                self.is_host = False
                self.status_message = f"Connected in {connect_time:.1f}s"
                
                logging.info(f"✅ CONNECTION SUCCESS! Time: {connect_time:.1f}s")
                print(f"✅ Connected to {host_ip} in {connect_time:.1f}s")
                
                # Set socket to non-blocking untuk game
                self.socket.setblocking(False)
                
                return True
                
            except socket.timeout as e:
                logging.warning(f"⏳ Timeout on attempt {attempt + 1}: {e}")
                print(f"⏳ Timeout on attempt {attempt + 1}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    self.error_message = f"Host not responding after {max_retries} attempts"
                    logging.error(self.error_message)
                    return False
                    
            except ConnectionRefusedError as e:
                logging.warning(f"🚫 Connection refused on attempt {attempt + 1}: {e}")
                print(f"🚫 Connection refused")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    self.error_message = "Connection refused - Host not running or firewall blocking"
                    logging.error(self.error_message)
                    return False
                    
            except Exception as e:
                logging.error(f"❌ Error on attempt {attempt + 1}: {e}")
                print(f"❌ Connection error: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    self.error_message = f"Connection failed: {str(e)}"
                    logging.error(self.error_message)
                    return False
        
        return False
    
    def _validate_ip(self, ip):
        """Validate IP address format"""
        import re
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(pattern, ip):
            parts = ip.split('.')
            try:
                return all(0 <= int(p) <= 255 for p in parts)
            except:
                return False
        return False
    
    def send_data(self, data):
        """Send data ke client/host - IMPROVED"""
        if self.connected and self.socket:
            try:
                data_str = str(data)
                data_bytes = data_str.encode('utf-8')
                length = len(data_bytes)
                
                # Format: [LENGTH(10 bytes)][DATA]
                self.socket.sendall(f"{length:10d}".encode() + data_bytes)
                return True
            except Exception as e:
                logging.error(f"Error sending data: {e}")
                self.connected = False
                return False
        return False
    
    def receive_data(self):
        """Receive data dari client/host - IMPROVED"""
        if self.connected and self.socket:
            try:
                # Receive length header
                length_data = self.socket.recv(10)
                if not length_data:
                    self.connected = False
                    return None
                
                try:
                    length = int(length_data.decode().strip())
                except ValueError:
                    logging.warning(f"Invalid length header: {length_data}")
                    return None
                
                # Receive all data (dengan retry untuk partial data)
                data = b""
                while len(data) < length:
                    chunk = self.socket.recv(min(1024, length - len(data)))
                    if not chunk:
                        self.connected = False
                        return None
                    data += chunk
                
                return data.decode('utf-8')
                
            except socket.timeout:
                pass  # Normal
            except BlockingIOError:
                pass  # Data belum ready
            except Exception as e:
                logging.error(f"Error receiving data: {e}")
                self.connected = False
                return None
    
    def send_player_position(self, player_id, x, y):
        """Kirim posisi player ke remote - FIXED"""
        if self.connected and self.socket:
            try:
                # Gunakan format yang sama dengan send_data()
                data = f"POS|{player_id}|{x}|{y}"
                data_bytes = data.encode('utf-8')
                length = len(data_bytes)
                
                # Kirim: [LENGTH(10 bytes)][DATA]
                self.socket.sendall(f"{length:10d}".encode() + data_bytes)
                return True
            except Exception as e:
                logging.error(f"Error sending position: {e}")
                self.connected = False
                return False
        return False

    def receive_player_position(self):
        """Terima posisi player dari remote - FIXED"""
        if self.connected and self.socket:
            try:
                # Receive length header (10 bytes)
                length_data = self.socket.recv(10)
                if not length_data:
                    self.connected = False
                    return None
                
                try:
                    length = int(length_data.decode().strip())
                except ValueError:
                    logging.warning(f"Invalid length header: {length_data}")
                    return None
                
                # Receive actual data
                data = b""
                while len(data) < length:
                    chunk = self.socket.recv(min(1024, length - len(data)))
                    if not chunk:
                        self.connected = False
                        return None
                    data += chunk
                
                data_str = data.decode('utf-8')
                
                if data_str.startswith("POS|"):
                    parts = data_str.split("|")
                    if len(parts) == 4:
                        try:
                            player_id = int(parts[1])
                            x = int(float(parts[2]))
                            y = int(float(parts[3]))
                            return (player_id, x, y)
                        except ValueError:
                            logging.warning(f"Invalid position data: {data_str}")
                            return None
            except socket.timeout:
                pass  # Normal untuk non-blocking socket
            except BlockingIOError:
                pass  # Data belum ready
            except Exception as e:
                logging.error(f"Error receiving position: {e}")
                self.connected = False
                return None
    
        return None

    def disconnect(self):
        """Disconnect from network"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.status_message = "Disconnected"
        
        # PERBAIKAN: Reset last_event juga
        if hasattr(self, 'last_event'):
            self.last_event = None
        
        # PERBAIKAN: Reset error message
        self.error_message = ""
    
    def get_connection_info(self):
        """Get connection info for UI display - IMPROVED"""
        info_lines = []
        
        if self.is_host:
            info_lines.append("ROLE: HOST")
            
            # PERBAIKAN: Tampilkan informasi IP yang lebih jelas
            if hasattr(self, 'zerotier_ip') and self.zerotier_ip:
                ip_text = self.zerotier_ip
                
                # Cek tipe IP
                if "Local IP:" in ip_text:
                    # Ini IP lokal, bukan ZeroTier
                    info_lines.append(f"WARNING: {ip_text}")
                    info_lines.append("Use ZeroTier for online play")
                elif "Error" in ip_text or "failed" in ip_text.lower():
                    info_lines.append("IP: Detection failed")
                    info_lines.append("Check ZeroTier installation")
                elif ip_text.startswith('192.168.191.'):
                    info_lines.append(f"ZeroTier IP: {ip_text}")
                elif any(ip_text.startswith(prefix) for prefix in ['10.', '172.', '192.168.']):
                    info_lines.append(f"Network IP: {ip_text}")
                    info_lines.append("(May work if player in same network)")
                else:
                    info_lines.append(f"IP: {ip_text}")
            else:
                info_lines.append("IP: Not detected")
            
            info_lines.append(f"Port: {self.port}")
            
            if self.connected:
                info_lines.append("STATUS: PLAYER CONNECTED")
            else:
                info_lines.append("STATUS: Waiting for player...")
        else:
            info_lines.append("ROLE: CLIENT")
            if self.connected:
                info_lines.append("STATUS: CONNECTED TO HOST")
            else:
                info_lines.append("STATUS: Not connected")
        
        # Tambahkan status/error message jika ada
        if self.status_message and self.status_message != "Not connected":
            info_lines.append(f"INFO: {self.status_message}")
        
        if self.error_message:
            # Potong error message jika terlalu panjang
            if len(self.error_message) > 40:
                error_display = self.error_message[:37] + "..."
            else:
                error_display = self.error_message
            info_lines.append(f"ERROR: {error_display}")
        
        # Log untuk debugging
        logging.debug(f"Connection info lines: {info_lines}")
                
        return info_lines
    
    def get_error_message(self):
        """Get detailed error message for display - IMPROVED VERSION"""
        if self.error_message:
            # PERBAIKAN: Kategorikan error message
            error_lower = self.error_message.lower()
            
            if "host cancelled" in error_lower:
                return "Host cancelled the game"
            elif "timeout" in error_lower or "not responding" in error_lower:
                return "Host not responding"
            elif "connection refused" in error_lower:
                return "Connection refused - Check IP and firewall"
            elif "invalid ip" in error_lower:
                return "Invalid IP address"
            elif "failed" in error_lower or "error" in error_lower:
                # Coba ekstrak informasi yang lebih spesifik
                if "socket" in error_lower or "network" in error_lower:
                    return "Network connection failed"
                elif "address" in error_lower:
                    return "Invalid network address"
                else:
                    # Potong error message jika terlalu panjang
                    if len(self.error_message) > 50:
                        return self.error_message[:47] + "..."
                    return self.error_message
            else:
                # Fallback
                return self.error_message
        return ""
    
    def send_control_scheme(self, control_scheme):
        """Kirim skema kontrol ke client (Host only)"""
        if self.is_host and self.connected:
            data = {
                'type': 'control_scheme',
                'scheme': control_scheme,
                'player_id': 2  # Selalu player 2 untuk client
            }
            self.send_data(json.dumps(data))
            return True
        return False
    
    def receive_control_scheme(self):
        """Terima skema kontrol dari host (Client only)"""
        if not self.is_host and self.connected:
            try:
                data = self.receive_data()
                if data:
                    data_dict = json.loads(data)
                    if data_dict.get('type') == 'control_scheme':
                        return data_dict.get('scheme', 'arrows')
            except:
                pass
        return None
    
    def send_event(self, event_type, payload=None):
        """Kirim event JSON kecil ke remote (type + payload)"""
        try:
            import json
            data = {'type': event_type, 'payload': payload or {}}
            data_str = json.dumps(data)
            
            # PERBAIKAN: Tambahkan newline sebagai delimiter
            data_str += '\n'
            
            # Kirim dengan try-catch
            if self.connected and self.socket:
                self.socket.sendall(data_str.encode('utf-8'))
                logging.debug(f"Event sent: {event_type}")
                return True
        except Exception as e:
            logging.error(f"send_event error: {e}")
            self.connected = False
        return False

    def receive_event(self):
        """
        Receive high-level event (JSON) if available.
        Returns dict {'type':..., 'payload':...} or None.
        Sets self.last_event for convenience.
        """
        try:
            import json
            data = self.receive_data()
            if not data:
                return None
            try:
                parsed = json.loads(data)
                # store last event for UI layers that inspect network_manager
                self.last_event = parsed
                return parsed
            except Exception as e:
                logging.warning(f"Invalid JSON event received: {e} -> {data}")
                return None
        except Exception as e:
            logging.error(f"receive_event error: {e}")
            return None
        
    def send_event_safe(self, event_type, payload=None):
        """Kirim event dengan error handling lebih baik"""
        try:
            import json
            data = {'type': event_type, 'payload': payload or {}}
            data_str = json.dumps(data)
            # Tambahkan newline untuk memudahkan parsing
            data_str += '\n'
            self.socket.sendall(data_str.encode('utf-8'))
            return True
        except Exception as e:
            logging.error(f"send_event_safe error: {e}")
            self.connected = False
            return False

    def receive_event_safe(self):
        """Terima event dengan newline sebagai delimiter"""
        try:
            import json
            # Baca sampai newline
            data = b""
            while True:
                chunk = self.socket.recv(1)
                if not chunk:
                    self.connected = False
                    return None
                if chunk == b'\n':
                    break
                data += chunk
            
            if data:
                parsed = json.loads(data.decode('utf-8'))
                self.last_event = parsed
                return parsed
        except socket.timeout:
            pass
        except BlockingIOError:
            pass
        except Exception as e:
            logging.error(f"receive_event_safe error: {e}")
        return None