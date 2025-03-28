import pygame
import random
import sys
def draw_window(snake, apple, score, high_score):
    # Clear the screen
    screen.fill((0, 0, 0))
    
    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, (0, 255, 0), (segment[0], segment[1], 20, 20))

    # Draw apple
    pygame.draw.rect(screen, (255, 0, 0), (apple[0], apple[1], 20, 20))

    # Draw score and high score
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    high_score_text = font.render(f'High Score: {high_score}', True, (255, 255, 255))
    screen.blit(high_score_text, (10, 30))

    pygame.display.flip()
    

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Snake Game')
font = pygame.font.Font(None, 36)

# Snake and apple variables
snake = [(300, 300)]
apple = (random.randint(0, 29) * 20, random.randint(0, 29) * 20)
direction = 'RIGHT'
score = 0
high_score = 0

# Game loop variables
clock = pygame.time.Clock()
game_over = False

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and direction != 'RIGHT':
                direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                direction = 'RIGHT'
            elif event.key == pygame.K_UP and direction != 'DOWN':
                direction = 'UP'
            elif event.key == pygame.K_DOWN and direction != 'UP':
                direction = 'DOWN'

    # Move snake
    if direction == 'LEFT':
        snake.insert(0, (snake[0][0] - 20, snake[0][1]))
    elif direction == 'RIGHT':
        snake.insert(0, (snake[0][0] + 20, snake[0][1]))
    elif direction == 'UP':
        snake.insert(0, (snake[0][0], snake[0][1] - 20))
    elif direction == 'DOWN':
        snake.insert(0, (snake[0][0], snake[0][1] + 20))

    # Check if snake ate the apple
    if snake[0] == apple:
        apple = (random.randint(0, 29) * 20, random.randint(0, 29) * 20)
        score += 1
        if score > high_score:
            high_score = score
    else:
        snake.pop()

    # Check for game over conditions
    if (snake[0][0] < 0 or snake[0][0] > 580 or
            snake[0][1] < 0 or snake[0][1] > 580 or
            snake[0] in snake[1:]):
        game_over = True

    # Draw the game
    draw_window(snake, apple, score, high_score)

    # Set the frame rate and delay
    clock.tick(10 + score / 10)

# Exit the game
pygame.quit()

# Print final score
print(f'Final score: {score}')
print(f'High score: {high_score}')