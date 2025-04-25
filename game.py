import pygame
import numpy as np
import math
import sys

class CarRacingGame:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Car Racing Game")
        
        # Track properties
        self.track_width = 200
        self.track_center_x = width // 2
        self.track_center_y = height // 2
        self.track_radius = 200
        
        # Car properties
        self.car_width = 40
        self.car_height = 20
        self.car_speed = 0
        self.car_angle = 0
        # Start player car on the track
        self.car_x = self.track_center_x + self.track_radius
        self.car_y = self.track_center_y
        self.max_speed = 5
        self.acceleration = 0.1
        self.deceleration = 0.05
        self.turn_speed = 3
        
        # AI car properties
        self.ai_car_x = self.track_center_x
        self.ai_car_y = self.track_center_y - self.track_radius
        self.ai_car_speed = 0
        self.ai_car_angle = 0
        self.ai_target_angle = 0
        self.ai_lap_progress = 0  # Track progress in degrees (0-360)
        self.ai_target_speed = self.max_speed * 0.8  # AI drives at 80% of max speed
        
        # Colors
        self.car_color = (255, 0, 0)  # Red for player car
        self.ai_car_color = (0, 0, 255)  # Blue for AI car
        self.track_color = (100, 100, 100)
        self.grass_color = (0, 100, 0)
        
        self.clock = pygame.time.Clock()
        self.running = True
        
    def reset(self):
        # Reset player car to starting position on track
        self.car_x = self.track_center_x + self.track_radius
        self.car_y = self.track_center_y
        self.car_speed = 0
        self.car_angle = 0
        
        # Reset AI car
        self.ai_car_x = self.track_center_x
        self.ai_car_y = self.track_center_y - self.track_radius
        self.ai_car_speed = 0
        self.ai_car_angle = 0
        self.ai_lap_progress = 0
        
    def _is_on_track(self, x, y):
        distance = math.sqrt((x - self.track_center_x)**2 + (y - self.track_center_y)**2)
        return (self.track_radius - self.track_width/2) <= distance <= (self.track_radius + self.track_width/2)
    
    def _keep_on_track(self, x, y, angle):
        # Calculate distance from track center
        distance = math.sqrt((x - self.track_center_x)**2 + (y - self.track_center_y)**2)
        
        # If car would move off track, adjust its position
        if distance > self.track_radius + self.track_width/2:
            # Too far out, move towards center
            angle_to_center = math.atan2(self.track_center_y - y, self.track_center_x - x)
            x = self.track_center_x + (self.track_radius + self.track_width/2 - 1) * math.cos(angle_to_center)
            y = self.track_center_y + (self.track_radius + self.track_width/2 - 1) * math.sin(angle_to_center)
        elif distance < self.track_radius - self.track_width/2:
            # Too far in, move away from center
            angle_to_center = math.atan2(self.track_center_y - y, self.track_center_x - x)
            x = self.track_center_x + (self.track_radius - self.track_width/2 + 1) * math.cos(angle_to_center)
            y = self.track_center_y + (self.track_radius - self.track_width/2 + 1) * math.sin(angle_to_center)
        
        return x, y, angle
    
    def _update_ai_car(self):
        # Update lap progress (0-360 degrees)
        self.ai_lap_progress = (self.ai_lap_progress + 1) % 360
        
        # Calculate target position on track
        target_angle = math.radians(self.ai_lap_progress)
        target_x = self.track_center_x + self.track_radius * math.cos(target_angle)
        target_y = self.track_center_y + self.track_radius * math.sin(target_angle)
        
        # Calculate angle to target
        dx = target_x - self.ai_car_x
        dy = target_y - self.ai_car_y
        target_angle = math.degrees(math.atan2(dy, dx))
        
        # Smoothly adjust AI car angle
        angle_diff = (target_angle - self.ai_car_angle + 180) % 360 - 180
        self.ai_car_angle += angle_diff * 0.1
        
        # Adjust speed based on turn sharpness
        turn_factor = 1 - min(abs(angle_diff) / 90, 1) * 0.5
        target_speed = self.ai_target_speed * turn_factor
        
        # Smoothly adjust speed
        self.ai_car_speed += (target_speed - self.ai_car_speed) * 0.1
        
        # Apply friction
        if abs(self.ai_car_speed) > 0:
            self.ai_car_speed *= 0.98
        
        # Calculate new position
        new_x = self.ai_car_x + self.ai_car_speed * math.cos(math.radians(self.ai_car_angle))
        new_y = self.ai_car_y + self.ai_car_speed * math.sin(math.radians(self.ai_car_angle))
        
        # Update position if it would keep car on track
        if self._is_on_track(new_x, new_y):
            self.ai_car_x = new_x
            self.ai_car_y = new_y
        else:
            # If new position would be off track, keep current position
            self.ai_car_speed *= 0.5  # Slow down when hitting track boundary
    
    def _draw_car(self, x, y, angle, color):
        # Create a surface for the car
        car_surface = pygame.Surface((self.car_width, self.car_height), pygame.SRCALPHA)
        
        # Draw the car body (rectangular part)
        pygame.draw.rect(car_surface, color, (0, 0, self.car_width * 0.7, self.car_height))
        
        # Draw the triangular front
        front_points = [
            (self.car_width * 0.7, 0),  # Top point
            (self.car_width * 0.7, self.car_height),  # Bottom point
            (self.car_width, self.car_height // 2)  # Front point
        ]
        pygame.draw.polygon(car_surface, color, front_points)
        
        # Rotate the car
        rotated_car = pygame.transform.rotate(car_surface, -angle)
        car_rect = rotated_car.get_rect(center=(int(x), int(y)))
        self.screen.blit(rotated_car, car_rect)
    
    def run(self):
        self.reset()
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
            
            # Get keyboard input
            keys = pygame.key.get_pressed()
            action = [0, 0]  # [acceleration, steering]
            
            if keys[pygame.K_UP]:
                action[0] = 1
            elif keys[pygame.K_DOWN]:
                action[0] = -1
            if keys[pygame.K_LEFT]:
                action[1] = -1
            elif keys[pygame.K_RIGHT]:
                action[1] = 1
            
            # Update player car
            self.car_speed += action[0] * self.acceleration
            self.car_speed = max(-self.max_speed, min(self.max_speed, self.car_speed))
            self.car_angle += action[1] * self.turn_speed
            
            if abs(self.car_speed) > 0:
                self.car_speed *= 0.98
            
            # Calculate new position
            new_x = self.car_x + self.car_speed * math.cos(math.radians(self.car_angle))
            new_y = self.car_y + self.car_speed * math.sin(math.radians(self.car_angle))
            
            # Update position if it would keep car on track
            if self._is_on_track(new_x, new_y):
                self.car_x = new_x
                self.car_y = new_y
            else:
                # If new position would be off track, keep current position
                self.car_speed *= 0.5  # Slow down when hitting track boundary
            
            # Update AI car
            self._update_ai_car()
            
            # Render
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
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CarRacingGame()
    game.run() 