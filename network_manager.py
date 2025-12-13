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
        self.last_event = None
        self.host_info = None

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
            # PERBAIKAN: Reset dulu sebelum mulai host baru
            self.reset_for_new_host()
            
            # Buat socket baru
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set socket options untuk firewall traversal
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if hasattr(socket, 'SO_KEEPALIVE'):
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Bind ke port
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(1)
            self.socket.settimeout(0.5)  # Non-blocking accept
            
            self.status_message = "Host started - Waiting for connection..."
            print(f"✅ Host started on port {self.port}")
            return True
            
        except Exception as e:
            self.error_message = f"Error starting host: {str(e)}"
            print(f"❌ Failed to start host: {e}")
            self.reset_connection()  # Reset jika gagal
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
                
                # PERBAIKAN TAMBAHAN: Set timeout untuk mencegah blocking
                self.client_socket.settimeout(0.1)
                
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
                timeout = 3 if attempt == 0 else 5
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
            except socket.error as e:
                # Hanya disconnect untuk error koneksi spesifik
                if e.errno in [10054, 10053, 10058]:  # WSAECONNRESET, WSAECONNABORTED, WSAESHUTDOWN
                    logging.error(f"Connection error: {e}")
                    self.connected = False
                else:
                    logging.warning(f"Socket error (non-fatal): {e}")
                return False
            except Exception as e:
                logging.error(f"Error sending data: {e}")
                # Jangan langsung disconnect untuk error umum
                return False
        return False
    
    def receive_data(self):
        """Receive data dari client/host - IMPROVED"""
        if self.connected and self.socket:
            try:
                # PERBAIKAN: Check if socket is still valid
                if not self.socket:
                    self.connected = False
                    return None
                
                # Set timeout untuk non-blocking read
                self.socket.settimeout(0.01)
                
                # Receive length header
                length_data = b""
                try:
                    # Try to read 10 bytes for length header
                    while len(length_data) < 10:
                        chunk = self.socket.recv(10 - len(length_data))
                        if not chunk:
                            # Connection closed by peer
                            self.connected = False
                            return None
                        length_data += chunk
                except socket.timeout:
                    # No data available yet, return None
                    return None
                except socket.error as e:
                    # Handle specific socket errors gracefully
                    if e.errno in [10035, 10054, 10053]:  # WSAEWOULDBLOCK, WSAECONNRESET, WSAECONNABORTED
                        if e.errno == 10054:  # Connection reset by peer
                            self.connected = False
                        return None
                    else:
                        logging.warning(f"Socket error in receive_data: {e}")
                        return None
                
                if not length_data:
                    return None
                
                try:
                    length = int(length_data.decode().strip())
                except ValueError:
                    logging.warning(f"Invalid length header: {length_data}")
                    return None
                
                # Receive all data
                data = b""
                attempts = 0
                max_attempts = 10  # Maksimal 10x coba baca
                
                while len(data) < length and attempts < max_attempts:
                    try:
                        chunk = self.socket.recv(min(1024, length - len(data)))
                        if not chunk:
                            if attempts > 5:  # Setelah 5x coba tanpa data
                                self.connected = False
                                return None
                            attempts += 1
                            continue
                        data += chunk
                    except socket.timeout:
                        attempts += 1
                        continue
                    except socket.error as e:
                        if e.errno in [10035, 10054, 10053]:
                            if e.errno == 10054:
                                self.connected = False
                            break
                        else:
                            logging.warning(f"Socket error reading data: {e}")
                            attempts += 1
                
                if len(data) < length:
                    return None  # Data tidak lengkap, coba lagi nanti
                
                return data.decode('utf-8')
                    
            except socket.timeout:
                return None  # Normal, no data yet
            except BlockingIOError:
                return None  # Data belum ready
            except Exception as e:
                logging.error(f"Error receiving data: {e}")
                # Jangan langsung disconnect untuk error kecil
                if "10035" not in str(e) and "10054" not in str(e):
                    # Hanya disconnect untuk error serius
                    if "Broken pipe" in str(e) or "Connection reset" in str(e):
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
        """Disconnect dari jaringan - PERBAIKAN: panggil reset"""
        print("🔌 Disconnecting from network...")
        self.reset_connection()  # Gunakan method reset yang sudah ada
        
        # PERBAIKAN: Reset semua atribut dengan jelas
        self.status_message = "Disconnected"
        self.error_message = ""
        
        print("✅ Disconnected successfully")
    
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
    
    def reset_connection(self):
        """Reset koneksi jaringan ke keadaan awal"""
        print("🔄 Resetting network connection...")
        
        # Reset semua status
        self.connected = False
        self.is_host = False
        self.status_message = "Not connected"
        self.error_message = ""
        
        # Close sockets
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        # Reset last_event
        if hasattr(self, 'last_event'):
            self.last_event = None
        
        print("✅ Network connection reset")
        return True
    
    def reset_for_new_host(self):
        """Reset khusus untuk memulai sebagai host baru"""
        print("🔄 Preparing for new host session...")
        
        # Reset status tapi tetap sebagai host
        self.reset_connection()
        self.is_host = True
        self.connected = False
        self.status_message = "Starting host..."
        self.error_message = ""
        
        # Refresh ZeroTier IP
        self.zerotier_ip = self.get_zerotier_ip()
        
        print(f"✅ Ready for new host session, IP: {self.zerotier_ip}")
        return True
    
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
        """Kirim event JSON kecil ke remote (type + payload) - DIPERBAIKI"""
        try:
            import json
            data = {'type': event_type, 'payload': payload or {}}
            data_str = json.dumps(data)
            
            # TAMBAHKAN newline sebagai delimiter
            data_str += '\n'
            
            # Kirim dengan error handling yang lebih baik
            if self.connected and self.socket:
                self.socket.sendall(data_str.encode('utf-8'))
                logging.debug(f"Event sent: {event_type}")
                return True
            else:
                logging.warning(f"Cannot send event, not connected: {event_type}")
                return False
                
        except Exception as e:
            logging.error(f"send_event error: {e}")
            # Jangan langsung set connected = False, biarkan method lain yang handle
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
                self.last_event = parsed
                
                # PERBAIKAN PENTING: Selalu update host_info jika event adalah host_info
                if parsed.get('type') == 'host_info':
                    self.host_info = parsed.get('payload', {})
                    print(f"📥 NetworkManager stored host_info: {self.host_info}")
                    # Simpan juga ke log untuk debugging
                    logging.info(f"Host info received: {self.host_info}")
                
                return parsed
            except Exception as e:
                logging.warning(f"Invalid JSON event received: {e} -> {data}")
                return None
        except Exception as e:
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
    
    def reset_host_info(self):
        """Reset host info"""
        self.host_info = None
        self.last_event = None
        print("🔄 Host info reset")