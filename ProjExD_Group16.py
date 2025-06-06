import os
import random
import sys
import random
import pygame as pg
import math

WIDTH = 800
HEIGHT = 600
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # スクリプトの場所に移動


#無敵処理
class Muteki:
    def __init__(self, img_path):
        self.image = pg.image.load(img_path)
        self.image = pg.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (-100, -100)  # 最初は非表示
        self.active = False
        self.start_time = 0
        self.duration = 300  # 無敵時間（3秒）
        self.respawn_interval = 1000  # アイテム再出現時間（5秒）
        self.last_taken_time = -self.respawn_interval  # 最初から出現できる

    def update(self, screen, kk_rct, kk_img, tmr):
        # アイテムが非表示かつ再出現タイミングなら再配置
        if self.rect.center == (-100, -100) and tmr - self.last_taken_time >= self.respawn_interval:
            self.rect.center = (random.randint(400, 700), random.randint(100, 500))

        # こうかとんがアイテムに当たったとき
        if kk_rct.colliderect(self.rect):
            self.active = True
            self.start_time = tmr
            self.last_taken_time = tmr
            self.rect.center = (-100, -100)  # 消す

        # 無敵時間が過ぎたら無敵解除
        if self.active and tmr - self.start_time > self.duration:
            self.active = False

        # アイテム描画
        if self.rect.center != (-100, -100):
            screen.blit(self.image, self.rect)

        # こうかとん描画（無敵なら光らせる）
        if self.active:
            flash_img = pg.Surface((kk_rct.width, kk_rct.height), pg.SRCALPHA)
            flash_img.fill((255, 255, 0, 128))  # 黄色半透明
            screen.blit(kk_img, kk_rct)
            screen.blit(flash_img, kk_rct)
        else:
            screen.blit(kk_img, kk_rct)
class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, 550

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class Kabe(pg.sprite.Sprite):
    """敵機に関するクラス"""
    imgs = [pg.image.load("fig/shougaibutu1.png") for _ in range(3)]  # 画像を1回だけ読み込む

    def __init__(self, size):
        super().__init__()
        img = random.choice(__class__.imgs)
        self.image = pg.transform.scale(img, size)
        self.rect = self.image.get_rect()
        
        # 敵を右端の外から出現させる
        self.rect.left = WIDTH - 100  # 画面の右端より外側から出現
        self.rect.centery = random.randint(50, HEIGHT - 50)  # 垂直位置はランダム
        
        self.vx, self.vy = -4, 0  # 左方向に移動
        self.state = "fly"
        self.interval = random.randint(50, 300)

    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        # 画面外に出たら削除
        if self.rect.right < 0:
            self.kill()
    
class Koukaton:#こうかとん 
    def __init__(self, num: int, xy: tuple[int, int]):
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False) # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img, # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9), # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9), # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9), # 左上
            (-1, 0): img0, # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9), # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9), # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9), # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 30
    def update(self, key_lst, walls: pg.sprite.Group):
        a = b = 0
        if key_lst[pg.K_UP]:
            b = -1
        if key_lst[pg.K_DOWN]:
            b = +1
        if key_lst[pg.K_LEFT]:
            a = -1
        if key_lst[pg.K_RIGHT]:
            a = +1
        self.dire = (a, b)
        if (a, b) != (0, 0):
            self.image = self.imgs.get((a, b), self.image)
            new_rect = self.rect.move(a * self.speed / 30, b * self.speed / 30)

            # 壁とぶつかっていない場合のみ位置更新
            if not any(new_rect.colliderect(kabe.rect) for kabe in walls):
                self.rect = new_rect

    # def update(self, key_lst, wall: Kabe):
    #     a = b = 0
    #     if key_lst[pg.K_UP]:
    #         b = -1
    #     if key_lst[pg.K_DOWN]:
    #         b = +1
    #     if key_lst[pg.K_LEFT]:
    #         a = -1
    #     if key_lst[pg.K_RIGHT]:
    #         a = +1
    #     self.dire = (a, b)
    #     if (a, b) != (0, 0):
    #         self.image = self.imgs.get((a, b), self.image)
    #         self.rect.move(a * self.speed / 30, b * self.speed / 30)
    #         new_rect = self.rect.move(a * self.speed / 30, b * self.speed / 30) 
    #         if not new_rect.colliderect(wall):
    #             self.rect = new_rect
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Koukaton, angle0: float=0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 1.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        self.state = "active"
    
    def update(self):
        self.rect.move_ip(self.vx * self.speed, self.vy * self.speed)
        if self.rect.left > WIDTH or self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()

# class Enemy:#敵
#     def __init__(self, xy):
#         self.image = pg.image.load("fig/enemy.png")  
#         self.rect = self.image.get_rect(center=xy)

#     def draw(self, screen):
#         screen.blit(self.image, self.rect)
    


    

class Enemy(pg.sprite.Sprite):
    """
    敵に関するクラス
    """
    
    def __init__(self):
        super().__init__()
        img = pg.image.load("fig/enemy.png")
        self.image = pg.transform.rotozoom(img, 0, 0.1)
        self.rect = self.image.get_rect()
        self.rect.center = 800, random.randint(0,600)
        self.vx, self.vy = -2 , 0
        self.up_down_moving = False  # 上下移動開始フラグ
        self.direction = 1  # 上下移動の方向（1:下, -1:上）
        self.base_y = self.rect.centery


        
    def update(self, tmr):
        """
        敵を右から左に移動させる
        時間経過で挙動変更
        """
        self.rect.move_ip(self.vx,self.vy)
        if tmr >= 2000:
            self.vx = -1.5
            self.up_down_moving = True

        if tmr >= 3500:
            self.vx = -2.5  # 移動速度をあげる

        if self.up_down_moving:
            self.vy = 1 * self.direction
            self.rect.move_ip(self.vx, self.vy)

            # 基準座標から方向転換
            if self.rect.centery > self.base_y + random.randint(300,500):
                self.direction = -1
            elif self.rect.centery < self.base_y - random.randint(300,500):
                self.direction = 1

            # 画面上端または下端で方向反転
            if self.rect.top <= 0:
                self.direction = 1
            elif self.rect.bottom >= 600:
                self.direction = -1
    def draw(self, screen):
        screen.blit(self.image, self.rect)

def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
 #無敵アイテム
    muteki_item = Muteki("fig/muteki_cake.jpg")
    # 背景画像

    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)

    # こうかとん画像
    kk_img = pg.image.load("fig/3.png")
    kk_img = pg.transform.flip(kk_img, True, False)
    kk_img = pg.transform.rotozoom(kk_img, 10, 1.0)
    kk_size = kk_img.get_size()  # 敵画像にも使うため保存    
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bird = Koukaton(3, (900, 400))
    beams = pg.sprite.Group()
    emys = pg.sprite.Group()

   

   
    score = Score() 
    

    kabes = pg.sprite.Group()
    bg_img2 = pg.transform.flip(bg_img, True, False)#練習８88888888888
    wall = pg.Rect(0, 0, 0, 0)


    kk_rct = kk_img.get_rect()#練習１０.１
    kk_rct.center = 300, 200#練習１０.２

    
    

    emys = pg.sprite.Group()
    

    
    kouka = Koukaton(3, (300, 200))
    enemy = Enemy()
    
    bg_img2 = pg.transform.flip(bg_img, True, False) 
    tmr = 0
    # score = 0

    muteki_item.update(screen, kk_rct, kk_img, tmr)


    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    beams.add(Beam(kouka))  # 通常ビーム
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_LCTRL:#左コントロールを押すと加速
                kouka.speed = 100
            if event.type == pg.KEYUP and event.key == pg.K_LCTRL:#元の速さ（押していないとき）
                kouka.speed = 30

        kouka.update(key_lst,kabes)

        
        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            score.value += 10

                   

        if kouka.rect.colliderect(enemy.rect):
            if not muteki_item.active:
                print("Game Over!")
                return

      

        key_lst = pg.key.get_pressed()#練習１０.４
       
        
            

        



        
        
        x = tmr%3200 #練習６ 練習９

        if tmr%400 == 0:    # 敵を2秒間隔で追加
            emys.add(Enemy())
       
        screen.blit(bg_img, [-x, 0]) #練習６
        screen.blit(bg_img2, [-x+1600 ,0])#練習７
        screen.blit(bg_img, [-x+3200, 0])#練習９

        # screen.blit(kk_img, [300, 200])#練習４

        if tmr % 200 == 0:
            kabes.add(Kabe(kk_size))  # 主人公サイズで敵を生成
            kabes.add(Kabe(kk_size))  # 主人公サイズで敵を生成
        kabes.update()
        kabes.draw(screen)

        for enemy in emys:
            enemy.update(tmr)
        emys.draw(screen)

        # screen.blit(kk_img, kk_rct)#練習１０.５

        beams.update()
        beams.draw(screen)
        kouka.draw(screen)
        enemy.draw(screen)
        pg.draw.rect(screen, (128, 64, 0), wall)

        screen.blit(bg_img, [-x, 0])
        screen.blit(bg_img2, [-x+1600 ,0])
        screen.blit(bg_img, [-x+3200, 0])

        if tmr % 200 == 0:
            kabes.add(Kabe(kk_size))
            kabes.add(Kabe(kk_size))
        kabes.update()
        kabes.draw(screen)

        for enemy in emys:
            enemy.update(tmr)
        emys.draw(screen)

        beams.update()
        beams.draw(screen)
        kouka.draw(screen)
        enemy.draw(screen)
        muteki_item.update(screen, kouka.rect, kouka.image, tmr)  # ★ ここを追加！
        pg.draw.rect(screen, (128, 64, 0), wall)

        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(200)


       
        
        pg.display.update()
        tmr += 1
        clock.tick(200)

        score.update(screen) #scoreを画面に表示
        pg.display.update()
        



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()

    