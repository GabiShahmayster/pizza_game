import pygame
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_LEFT, K_RIGHT, K_DOWN, K_UP, K_q
# from cv.ColorTuple import ColorTuple as ColorBGR
from typing import Tuple, Type, Optional, List
# from cv.VideoStreamReader import VideoStreamReader, FrameInformation, waitKey
# from cv2 import imshow, COLOR_BGR2RGB, cvtColor
import numpy as np

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# def bgr_to_rgb(color: ColorBGR) -> Tuple:
#     """
#     This method convert openCV BGR colors to RGB colors
#     @param color:
#     @return:
#     """
#     return color.value[2], color.value[1], color.value[0]


ACCELERATION_DICT = {K_LEFT: np.array([-1, 0]),
                     K_RIGHT: np.array([1, 0]),
                     K_UP: np.array([0, -1]),
                     K_DOWN: np.array([0, 1])}


class PyGameObject:
    """
    This class provides a simple wrapper to PyGame objects
    """
    pygame_object: object
    # color: ColorBGR

    velocity_vector: np.ndarray
    target_position: np.ndarray

    MAX_SPEED_PIXEL_PER_FRAME: int = 10
    disable_acceleration_flag: bool
    axes_constaint: np.ndarray

    img_object: pygame.Surface


    def __init__(self, pygame_object: object,
                 img_object: pygame.Surface,
                 color: tuple = WHITE,
                 initial_velocity_vector: np.ndarray = None):
        if initial_velocity_vector is None:
            initial_velocity_vector = np.zeros(2)

        self.pygame_object = pygame_object
        self.color = color
        self.velocity_vector = initial_velocity_vector
        self.target_position = np.array([pygame_object.x, pygame_object.y])
        self.disable_acceleration_flag = False
        self.axes_constaint = np.array([1, 1])

        self.img_object = img_object

    def is_collided_with(self, target: 'PyGameRectangle'):
        return self.pygame_object.colliderect(target.pygame_object)

    def make_horizontal(self):
        self.axes_constaint = np.array([1, 0])

    def make_vertical(self):
        self.axes_constaint = np.array([0, 1])

    def disable_acceleration(self):
        self.disable_acceleration_flag = True

    def enable_acceleration(self):
        self.disable_acceleration_flag = False

    def update(self, display: pygame.Surface):
        # self.update_acceleration()
        self.update_velocity()
        if self.velocity_vector[0] != 0 or self.velocity_vector[1] != 0:
            self.pygame_object.move_ip((self.velocity_vector[0], self.velocity_vector[1]))
        self.draw(display=display)
        display.blit(self.img_object, self.pygame_object)

    def draw(self, display: pygame.Surface):
        """
        This method draws the object
        @return:
        """
        pygame.draw.rect(display, self.color, self.pygame_object)

    def accelerate(self, acceleration: np.ndarray):
        # https: // github.com / Mekire / pygame - samples / blob / master / eight_dir_move.py
        if not self.disable_acceleration_flag:
            # for key, acceleration in ACCELERATION_DICT.items():
            #     if pressed_keys[key]:
            new_velocity = self.velocity_vector + np.diag(self.axes_constaint) @ acceleration
            if np.sqrt(new_velocity.T @ new_velocity) < self.MAX_SPEED_PIXEL_PER_FRAME:
                self.velocity_vector = new_velocity

    def stop_motion(self):
        self.velocity_vector = (0, 0)



    def move_to_position(self, mouse_position: np.ndarray):
        self.target_position = mouse_position

    def update_acceleration(self):
        K = 1 / 100
        object_position = np.array([self.pygame_object.x, self.pygame_object.y])
        acceleration = K * np.diag(self.axes_constaint) @ \
                       (self.target_position - object_position)
        self.accelerate(acceleration=acceleration)

    def update_velocity(self):
        if self.disable_acceleration_flag:
            return
        K = 1 / 10
        object_position = np.array([self.pygame_object.x, self.pygame_object.y])
        velocity = K * np.diag(self.axes_constaint) @ \
                       (self.target_position - object_position)
        self.velocity_vector = velocity


class PyGameRectangle(PyGameObject):

    def __init__(self,
                 left: int,
                 top: int,
                 width: int,
                 height: int,
                 img_object: pygame.Surface,
                 rectangle: pygame.Rect = None,
                 initial_velocity_vector: np.ndarray = None):
        if rectangle is None:
            rectangle = pygame.rect.Rect(left, top, width, height)
        super().__init__(pygame_object=rectangle,
                         img_object=img_object,
                         initial_velocity_vector=initial_velocity_vector)

class PizzaObject(PyGameRectangle):
    pass

class TunaObject(PyGameRectangle):
    pass

def event_handler(rect: Type[PyGameObject]):
    for event in pygame.event.get():
        if event.type == QUIT or (
                event.type == KEYDOWN and (
                event.key == K_ESCAPE or
                event.key == K_q
        )):
            pygame.quit()
            quit(0)

        # ____KEYS____
        # if event.type in (KEYDOWN, KEYUP):
        #     keys = pygame.key.get_pressed()

        # ____MOUSE MOTION->ACCELERATION____
        # acceleration = np.asarray(pygame.mouse.get_rel())
        # rect.accelerate(acceleration=acceleration)

        # ____MOUSE DISTANCE FROM CURRENT LOCATION->ACCELERATION____
        mouse_position = np.asarray(pygame.mouse.get_pos())
        rect.move_to_position(mouse_position)


if __name__ == "__main__":

    # webcam_stream: VideoStreamReader = VideoStreamReader(0)
    # webcam_stream.disable_user_input_handling()
    # webcam_stream.disable_frame_overlay()
    # screen_width = webcam_stream.get_frame_width()
    # screen_height = webcam_stream.get_frame_height()
    # FPS = webcam_stream.get_frames_per_second()

    pygame.init()
    FPS = 30
    # delay_msec = 1
    # interval_msec = int(1000*1/FPS)
    # pygame.key.set_repeat(delay_msec, interval_msec)

    screen_width = 2 * 640
    screen_height = 2 * 480
    fpsClock = pygame.time.Clock()

    # rect: PyGameRectangle = PyGameRectangle(left=10, top=10, width=10, height=10)

    pygame.display.set_caption('webcam')
    screen = pygame.display.set_mode((screen_width, screen_height))

    font = pygame.font.SysFont('David.ttf', 32)

    pygame.mixer.init()
    pygame.mixer.music.load('/home/gabi/Desktop/game/hasidim.ogg')
    pygame.mixer.music.play(-1)
    eat_pizza_sound = pygame.mixer.Sound('/home/gabi/Desktop/game/eat_cake.wav')
    eat_tuna_sound = pygame.mixer.Sound('/home/gabi/Desktop/game/eat_tuna.wav')
    pizza_img = pygame.image.load("/home/gabi/Desktop/game/cake.png")
    pizza_counter_img = pizza_img.get_rect(top=0,left=0)
    tuna_img = pygame.image.load("/home/gabi/Desktop/game/tuna.png")
    tuna_counter_img = tuna_img.get_rect(top=50, left=0)
    list_of_falling_objects: List[PyGameRectangle] = list()
    # for falling_object_left in range(pizza_img.get_width(), screen_width - pizza_img.get_width(), 100):


    girl_img = pygame.image.load("/home/gabi/Desktop/game/romi_face.png")
    girl_rect = PyGameRectangle(left=-1, top=-1, width=-1, height=-1,
                                rectangle=girl_img.get_rect(top=screen_height - girl_img.get_height(),
                                                            left=0),
                                img_object=girl_img,
                                initial_velocity_vector=np.array([0, 0]))
    # girl_rect.make_horizontal()
    number_of_pizzas = 0
    number_of_tunas = 0
    current_time = pygame.time.get_ticks()
    time_to_next_falling_object_msec = 500
    next_falling_object_appearance_time = current_time + time_to_next_falling_object_msec
    while True:
        if pygame.time.get_ticks() > next_falling_object_appearance_time:
            next_falling_object_appearance_time += time_to_next_falling_object_msec
            vertical_speed = np.random.random_integers(low=1, high=3, size=1)[0]
            horizontal_coord_of_falling_object = screen_width*np.random.uniform(size=1)

            random_object_flag = np.random.binomial(n=1,
                                                    p=0.5,
                                                    size=1)[0]
            if random_object_flag == 0:
                # pizza
                temp_pizza = PizzaObject(left=-1, top=-1, width=-1, height=-1,
                                         img_object=pizza_img,
                                         rectangle=pizza_img.get_rect(top=0, left=horizontal_coord_of_falling_object),
                                         initial_velocity_vector=np.array([0, vertical_speed]))

                temp_pizza.disable_acceleration()
                list_of_falling_objects.append(temp_pizza)
            else:
                # tuna
                temp_tuna = TunaObject(left=-1, top=-1, width=-1, height=-1,
                                       img_object=tuna_img,
                                       rectangle=tuna_img.get_rect(top=0, left=horizontal_coord_of_falling_object),
                                       initial_velocity_vector=np.array([0, vertical_speed]))

                temp_tuna.disable_acceleration()
                list_of_falling_objects.append(temp_tuna)

        screen.fill(color=BLACK)
        frame_rect = screen.get_rect()

        # frame_information: FrameInformation = next(webcam_stream)
        # frame = cvtColor(frame_information.frame, COLOR_BGR2RGB)
        # frame = np.fliplr(frame)
        # frame = np.rot90(frame)
        # frame_surface = pygame.surfarray.make_surface(frame)
        # frame_rect = frame_surface.get_rect()

        for falling_object in list(list_of_falling_objects):
            # pizza.pygame_object.clamp_ip(frame_rect)
            if not falling_object.is_collided_with(girl_rect):
                falling_object.update(display=screen)
            else:
                if type(falling_object) is PizzaObject:
                    eat_pizza_sound.play()
                    number_of_pizzas += 1
                elif type(falling_object) is TunaObject:
                    eat_tuna_sound.play()
                    number_of_tunas += 1
                list_of_falling_objects.remove(falling_object)

        event_handler(girl_rect)
        girl_rect.pygame_object.clamp_ip(frame_rect)
        girl_rect.update(display=screen)
        screen.blit(screen, (0, 0))
        screen.blit(screen, frame_rect)
        screen.blit(pizza_img, pizza_counter_img)
        screen.blit(tuna_img, tuna_counter_img)
        screen.blit(girl_img, girl_rect.pygame_object)

        number_of_pizzas_text = font.render('{0:d}'.format(number_of_pizzas), True, WHITE)
        number_of_pizzas_text_rect = number_of_pizzas_text.get_rect()
        number_of_pizzas_text_rect.center = (pizza_counter_img.x+pizza_img.get_width()+10,
                                             pizza_counter_img.y+pizza_img.get_height()/2)
        screen.blit(number_of_pizzas_text, number_of_pizzas_text_rect)

        number_of_tunas_text = font.render('        {0:d}'.format(number_of_tunas), True, WHITE)
        number_of_tunas_text_rect = number_of_tunas_text.get_rect()
        number_of_tunas_text_rect.center = (tuna_counter_img.x+tuna_img.get_width()+10,
                                             tuna_counter_img.y+tuna_img.get_height()/2)
        screen.blit(number_of_tunas_text, number_of_tunas_text_rect)

        # rect.update()
        pygame.display.flip()
        fpsClock.tick(FPS)

        # imshow('webcam', frame_information.frame)
        # waitKey(int(1000*1/FPS))
