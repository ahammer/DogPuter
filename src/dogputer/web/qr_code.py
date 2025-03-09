"""
QR Code generation utilities for the DogPuter web interface
"""

import io
import socket
import pygame

# Try to import QR code libraries, but don't fail if they're not available
try:
    import qrcode
    from PIL import Image
    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False

def get_local_ip():
    """
    Get the local IP address of the device
    
    Returns:
        str: Local IP address
    """
    try:
        # Create a socket to determine the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable, just used to determine the interface
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'  # Fallback to localhost
    finally:
        s.close()
    return ip

def generate_qr_code(data, size=150, margin=32):
    """
    Generate a QR code as a Pygame surface
    
    Args:
        data (str): The data to encode in the QR code
        size (int): The size of the QR code in pixels
        margin (int): Margin around the QR code in pixels
        
    Returns:
        pygame.Surface: QR code as a Pygame surface or fallback surface if libraries unavailable
    """
    if not QR_CODE_AVAILABLE:
        # Create a simple fallback QR-like image if libraries aren't available
        print("QR code libraries not available. Using fallback.")
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        surface.fill((255, 255, 255))  # White background
        
        # Draw a black border
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(0, 0, size, size), 4)
        
        # Draw some squares to make it look QR-like
        square_size = size // 10
        patterns = [
            (0, 0), (1, 0), (2, 0),
            (0, 1), (0, 2),
            (7, 0), (8, 0), (9, 0),
            (9, 1), (9, 2),
            (0, 7), (0, 8), (0, 9),
            (1, 9), (2, 9),
            (5, 5), (5, 6), (6, 5)
        ]
        
        for x, y in patterns:
            pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(
                x * square_size, y * square_size, square_size, square_size
            ))
        
        # Draw text indication
        font = pygame.font.SysFont(None, size // 8)
        text = font.render("URL", True, (0, 0, 0))
        text_rect = text.get_rect(center=(size // 2, size // 2))
        surface.blit(text, text_rect)
        
        return surface
        
    # If QR code libraries are available, generate a proper QR code
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create PIL image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to the specified size
        img = img.resize((size, size))
        
        # Convert PIL image to Pygame surface
        byte_io = io.BytesIO()
        img.save(byte_io, format='PNG')
        byte_io.seek(0)
        
        # Load the QR code without adding a background
        qr_surface = pygame.image.load(byte_io)
        
        # Create a surface with margin but keep it transparent
        qr_size = qr_surface.get_size()
        surface_with_margin = pygame.Surface((qr_size[0] + margin*2, qr_size[1] + margin*2), pygame.SRCALPHA)
        surface_with_margin.blit(qr_surface, (margin, margin))
        
        return surface_with_margin
    except Exception as e:
        print(f"QR code generation failed: {e}")
        # Fall back to simple QR-like image on error
        return pygame.Surface((size, size))
