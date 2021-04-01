def is_ip_valid(ip):
    if ip == 'localhost':
        return True
    elif ip is None:
        return False
    elif type(ip) != str:
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            val = int(part)
            if not (0 <= val <= 255):
                return False
        except ValueError as e:
            return False
    return True