import pygame

class ViewState:
    """View state class containing all elements to be rendered"""
    
    def __init__(self):
        """Initialize the view state"""
        self.background_color = None
        self.video_frame = None
        self.feedback_text = None
        self.feedback_rect = None
        self.waiting_text = None
        self.waiting_text_rect = None

class ViewStateGenerator:
    """View state generator class for DogPuter"""
    
    def __init__(self, screen_width, screen_height):
        """Initialize the view state generator"""
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def generate_view_state(self, app_state):
        """Generate view state from application state"""
        view_state = ViewState()
        
        # Set background color
        view_state.background_color = app_state.background_color
        
        # Set video frame if playing
        view_state.video_frame = app_state.video_frame
        
        # Set feedback text if active
        view_state.feedback_text = app_state.feedback_surface
        view_state.feedback_rect = app_state.feedback_rect
        
        # Set waiting text if in waiting mode
        if app_state.mode.name == "WAITING":
            view_state.waiting_text = app_state.waiting_text_surface
            view_state.waiting_text_rect = app_state.waiting_text_rect
        
        return view_state
