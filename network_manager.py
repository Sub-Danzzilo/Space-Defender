import socket
import threading
import time
import pygame
import subprocess
import platform
import logging
import json
import psutil
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
                return True
            except socket.timeout:
                pass  # No connection yet
            except Exception as e:
                self.error_message = f"Connection error: {str(e)}"
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
                timeout = 20 if attempt == 0 else 30
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
        """Send data to client/host"""
        if self.connected and self.socket:
            try:
                # Simple protocol: send length first, then data
                data_str = str(data)
                length = len(data_str)
                self.socket.sendall(f"{length:10d}".encode() + data_str.encode())
                return True
            except:
                self.connected = False
                self.error_message = "Connection lost"
                return False
    
    def receive_data(self):
        """Receive data from client/host"""
        if self.connected and self.socket:
            try:
                # Receive length first
                length_data = self.socket.recv(10)
                if not length_data:
                    self.connected = False
                    self.error_message = "Connection closed by peer"
                    return None
                
                length = int(length_data.decode().strip())
                data = self.socket.recv(length).decode()
                return data
            except:
                self.connected = False
                self.error_message = "Connection lost"
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
        """Get detailed error message for display"""
        if self.error_message:
            if "timeout" in self.error_message.lower():
                return "Timeout - Host not responding"
            elif "refused" in self.error_message.lower():
                return "Connection refused - Check IP"
            elif "failed" in self.error_message.lower():
                return "Connection failed"
            else:
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
    
    def send_player_position(self, player_id, x, y):
        """Kirim posisi player ke remote"""
        if self.connected and self.socket:
            try:
                data = f"POS|{player_id}|{x}|{y}"
                self.socket.sendall(data.encode('utf-8'))
                return True
            except:
                return False
        return False

    def receive_player_position(self):
        """Terima posisi player dari remote"""
        if self.connected and self.socket:
            try:
                # ❌ JANGAN set non-blocking setiap kali dipanggil!
                # self.socket.setblocking(False)  # Ini sudah set di connect_to_host
                data = self.socket.recv(1024).decode('utf-8')
                if data.startswith("POS|"):
                    parts = data.split("|")
                    if len(parts) == 4:
                        player_id = int(parts[1])
                        x = int(float(parts[2]))
                        y = int(float(parts[3]))
                        return (player_id, x, y)
            except:
                pass
        return None