import pygame
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

# Your Mandelbrot setup
k = 200
center = np.array([-0.5, 0.0])
radius = np.array([1.5, 1.0])
num = np.array([3,2]) * k
maxiter = 10

start = center - radius
stop = center + radius

def get_complex_plane(start, stop, num):
    x_space = np.linspace(start[0], stop[0], int(num[0]))
    y_space = np.linspace(start[1], stop[1], int(num[1]))
    real, imag = np.meshgrid(x_space, y_space[::-1])
    return real + 1j*imag

def f(z,c,x): 
    return z**x + c

def apply_n_times(z,c,n,x):
    escape = np.zeros_like(c, dtype=float)
    for _ in range(n):
        z = f(z,c,x)
        escape[np.abs(z) < 2] += 1
    return escape

cmaps = plt.colormaps()

def mandelbrot_surface(escape, maxiter, cmap_index=0):
    norm = escape / maxiter

    cmap = cm.get_cmap(cmaps[cmap_index])
    colors = cmap(norm)
    colors = (colors[:, :, :3] * 255).astype(np.uint8)
    return pygame.surfarray.make_surface(colors.swapaxes(0,1))

# --- Compute Mandelbrot ---
c = get_complex_plane(start, stop, num)
z = np.zeros_like(c)
x = 2
escape = apply_n_times(z, c, maxiter,x)

# --- Pygame init ---
pygame.init()
screen = pygame.display.set_mode((int(num[0]), int(num[1])))
surf = mandelbrot_surface(escape, maxiter)
my_font = pygame.font.SysFont('Comic Sans MS', 20)

zoom_factor = 0.5
pan_factor = 0.3 

cmi = 0

show_menu = True

parameterized = "c"


x_var = complex(2, 0)
c_var = complex(0, 0)
z_var = complex(0, 0)

param_keys = {"c":[pygame.K_i, pygame.K_k, pygame.K_o, pygame.K_l],
              "z":[pygame.K_y, pygame.K_h, pygame.K_u, pygame.K_j],
              "x":[pygame.K_r, pygame.K_f, pygame.K_t, pygame.K_g]}

running = True
while running:
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        center[0] -= radius[0] * pan_factor
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        center[0] += radius[0] * pan_factor
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        center[1] += radius[1] * pan_factor
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        center[1] -= radius[1] * pan_factor
    elif keys[pygame.K_q]:
        radius *= zoom_factor
    elif keys[pygame.K_e]:
        radius /= zoom_factor
    
    for var, key in param_keys.items():
        if parameterized != var:
            if keys[key[0]]:
                if var == "c":
                    c_var += complex(0.1, 0)
                elif var == "z":
                    z_var += complex(0.1, 0)
                else:
                    x_var += complex(0.1, 0)
            elif keys[key[1]]:
                if var == "c":
                    c_var -= complex(0.1, 0)
                elif var == "z":
                    z_var -= complex(0.1, 0)
                else:
                    x_var -= complex(0.1, 0)
            elif keys[key[2]]:
                if var == "c":
                    c_var += complex(0, 0.1)
                elif var == "z":
                    z_var += complex(0, 0.1)
                else:
                    x_var += complex(0, 0.1)
            elif keys[key[3]]:
                if var == "c":
                    c_var -= complex(0, 0.1)
                elif var == "z":
                    z_var -= complex(0, 0.1)
                else:
                    x_var -= complex(0, 0.1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key ==pygame.K_PLUS or event.key==pygame.K_EQUALS:
                maxiter += 5
            elif event.key==pygame.K_MINUS:
                maxiter  = max(10, maxiter-5)
            elif event.key==pygame.K_c:
                cmi += 1
                cmi = cmi%len(cmaps)
            elif event.key == pygame.K_m:
                show_menu = not show_menu
            elif event.key == pygame.K_p:
                if parameterized == "c":
                    parameterized = "z"
                elif parameterized == "z":
                    parameterized = "x"
                else:
                    parameterized = "c"
            elif event.key==pygame.K_RETURN:
                center = np.array([-0.5, 0.0])
                radius = np.array([1.5, 1.0])
                maxiter = 10
                cmi = 0
                parameterized = "c"
                                
                x_var = complex(2, 0)
                c_var = complex(0, 0)
                z_var = complex(0, 0)
        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:  # Left click = zoom in
                mx, my = pygame.mouse.get_pos()
                ''' this is a bit buggy
                # Map mouse pixel -> complex number
                x = start[0] + mx / num[0] * (stop[0] - start[0])
                y = start[1] + my / num[1] * (stop[1] - start[1])
                center = np.array([x, y])
                '''
                radius *= zoom_factor
            elif event.y==-1:
                radius /= zoom_factor

    
    # Recompute boundaries
    start = center - radius
    stop = center + radius
    if parameterized == "c":
        c = get_complex_plane(start, stop, num)
        z = np.full_like(c, z_var)
        x = x_var
    elif parameterized == "z":
        z = get_complex_plane(start, stop, num)
        c = np.full_like(z, c_var)
        x = x_var
    else:  # x parameterized
        x = get_complex_plane(start, stop, num)
        c = np.full_like(x,c_var)
        z = np.full_like(x,z_var)
    
    escape = apply_n_times(z, c, maxiter, x)

    surf = mandelbrot_surface(escape, maxiter, cmi)
    screen.blit(surf, (0, 0))

    #show stats
    if show_menu:
        screen.blit(my_font.render('Scroll/q/e:zoom, arrow keys/wasd:move, c:change colors, p:switch params, enter:reset', False, (255,255,255)), (0,0))
        screen.blit(my_font.render(f'max_iter: {maxiter} (+/-)', False, (255,255,255)), (0,40))
        screen.blit(my_font.render(f'Toggle menu: m', False, (255,255,255)), (0,60))

    screen.blit(my_font.render(f'(y/h,u/j) z: {"parameterized" if parameterized=="z" else f"{z_var.real:.1f},{z_var.imag:.1f}i"}', False, (255,255,255)), (0,120))
    screen.blit(my_font.render(f'(i/k,o/l) c: {"parameterized" if parameterized=="c" else f"{c_var.real:.1f},{c_var.imag:.1f}i"}', False, (255,255,255)), (0,140))
    screen.blit(my_font.render(f'(r/f,t/g) x: {"parameterized" if parameterized=="x" else f"{x_var.real:.1f},{x_var.imag:.1f}i"}', False, (255,255,255)), (0,160))

    pygame.display.flip()