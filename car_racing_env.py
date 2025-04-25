import pygame
import numpy as np
import math

class CarRacingEnv:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Car Racing Game")
        
        # Car properties
        self.car_width = 40
        self.car_height = 20
        self.car_speed = 0
        self.car_angle = 0
        self.car_x = width // 2
        self.car_y = height // 2
        self.max_speed = 5
        self.acceleration = 0.1
        self.deceleration = 0.05
        self.turn_speed = 3
        
        # AI car properties
        self.ai_car_x = width // 4
        self.ai_car_y = height // 4
        self.ai_car_speed = 0
        self.ai_car_angle = 0
        
        # Track properties
        self.track_width = 200
        self.track_center_x = width // 2
        self.track_center_y = height // 2
        self.track_radius = 200
        
        # Colors
        self.car_color = (255, 0, 0)  # Red for player car
        self.ai_car_color = (0, 0, 255)  # Blue for AI car
        self.track_color = (100, 100, 100)
        self.grass_color = (0, 100, 0)
        
        self.clock = pygame.time.Clock()
        self.running = True
        
    def reset(self):
        self.car_x = self.width // 2
        self.car_y = self.height // 2
        self.car_speed = 0
        self.car_angle = 0
        self.ai_car_x = self.width // 4
        self.ai_car_y = self.height // 4
        self.ai_car_speed = 0
        self.ai_car_angle = 0
        self.running = True
        return self._get_state()
    
    def _get_state(self):
        # Return state as numpy array
        return np.array([
            self.car_x / self.width,
            self.car_y / self.height,
            self.car_speed / self.max_speed,
            self.car_angle / 360,
            self.ai_car_x / self.width,
            self.ai_car_y / self.height,
            self.ai_car_speed / self.max_speed,
            self.ai_car_angle / 360
        ])
    
    def step(self, action):
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                return self._get_state(), 0, True
        
        if not self.running:
            return self._get_state(), 0, True
            
        # Action: [acceleration, steering]
        # acceleration: -1 (brake) to 1 (accelerate)
        # steering: -1 (left) to 1 (right)
        
        # Update player car
        self.car_speed += action[0] * self.acceleration
        self.car_speed = max(-self.max_speed, min(self.max_speed, self.car_speed))
        self.car_angle += action[1] * self.turn_speed
        
        # Apply friction/drag
        if abs(self.car_speed) > 0:
            self.car_speed *= 0.98
        
        # Update AI car (simple follow-the-track behavior)
        self._update_ai_car()
        
        # Update positions
        self.car_x += self.car_speed * math.cos(math.radians(self.car_angle))
        self.car_y += self.car_speed * math.sin(math.radians(self.car_angle))
        
        # Keep cars within screen bounds
        self.car_x = max(0, min(self.width, self.car_x))
        self.car_y = max(0, min(self.height, self.car_y))
        self.ai_car_x = max(0, min(self.width, self.ai_car_x))
        self.ai_car_y = max(0, min(self.height, self.ai_car_y))
        
        # Check if cars are on track
        player_on_track = self._is_on_track(self.car_x, self.car_y)
        ai_on_track = self._is_on_track(self.ai_car_x, self.ai_car_y)
        
        # Calculate reward
        reward = 0
        if player_on_track:
            reward += 0.1
            # Add speed bonus
            reward += abs(self.car_speed) * 0.01
        else:
            reward -= 0.1
            
        # Check if game is done
        done = not player_on_track
        
        # Render at consistent frame rate
        self.clock.tick(60)
        
        return self._get_state(), reward, done
    
    def _is_on_track(self, x, y):
        distance = math.sqrt((x - self.track_center_x)**2 + (y - self.track_center_y)**2)
        return abs(distance - self.track_radius) < self.track_width / 2
    
    def _update_ai_car(self):
        # Simple AI that follows the track
        angle_to_center = math.degrees(math.atan2(self.track_center_y - self.ai_car_y,
                                                 self.track_center_x - self.ai_car_x))
        distance = math.sqrt((self.ai_car_x - self.track_center_x)**2 + 
                           (self.ai_car_y - self.track_center_y)**2)
        
        # Adjust speed based on distance from track center
        target_speed = self.max_speed * (1 - abs(distance - self.track_radius) / (self.track_width / 2))
        self.ai_car_speed += (target_speed - self.ai_car_speed) * 0.1
        
        # Apply friction/drag to AI car
        if abs(self.ai_car_speed) > 0:
            self.ai_car_speed *= 0.98
        
        # Update position
        self.ai_car_x += self.ai_car_speed * math.cos(math.radians(angle_to_center))
        self.ai_car_y += self.ai_car_speed * math.sin(math.radians(angle_to_center))
        self.ai_car_angle = angle_to_center
    
    def render(self):
        if not self.running:
            return
            
        self.screen.fill(self.grass_color)
        
        # Draw track
        pygame.draw.circle(self.screen, self.track_color,
                         (int(self.track_center_x), int(self.track_center_y)),
                         self.track_radius + self.track_width // 2)
        pygame.draw.circle(self.screen, self.grass_color,
                         (int(self.track_center_x), int(self.track_center_y)),
                         self.track_radius - self.track_width // 2)
        
        # Draw cars
        self._draw_car(self.car_x, self.car_y, self.car_angle, self.car_color)
        self._draw_car(self.ai_car_x, self.ai_car_y, self.ai_car_angle, self.ai_car_color)
        
        pygame.display.flip()
    
    def _draw_car(self, x, y, angle, color):
        car_surface = pygame.Surface((self.car_width, self.car_height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, color, (0, 0, self.car_width, self.car_height))
        rotated_car = pygame.transform.rotate(car_surface, -angle)
        car_rect = rotated_car.get_rect(center=(int(x), int(y)))
        self.screen.blit(rotated_car, car_rect)
    
    def close(self):
        self.running = False
        pygame.quit() 