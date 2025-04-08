#       .--.
#   .-"     "-.
#  /  o     o  \
# |            |   < CHOMP!
# |  \     /  |
# \  '---'  /
#  '-.___.-'   > MAZE MAN RPG
# By Eli & Son
import pyxel

class App():
    def __init__(self):
        pyxel.init(180,128,title="Maze Man RPG",fps=24)
        pyxel.load("maze-man-rpg.pyxres")
        self.is_gaming = True
        self.in_battle = False
        self.battle_step = 0
        self.battle_counter = 0
        self.player_hp = 20
        self.enemy_hp = 10
        self.battle_text = ""
        self.battle_options = ["ATTACK", "MAGIC", "RUN"]
        self.selected_option = 0
        self.KEY = [pyxel.KEY_UP,pyxel.KEY_RIGHT,pyxel.KEY_DOWN,pyxel.KEY_LEFT]
        self.GPAD = [
                     pyxel.GAMEPAD1_BUTTON_DPAD_UP,
                     pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
                     pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                     pyxel.GAMEPAD1_BUTTON_DPAD_LEFT
        ]
        self.D = [[0,0],[0,-1],[1,0],[0,1],[-1,0]]
        self.high_score = 0
        self.score = 0
        self.init_stage()
        pyxel.run(self.update,self.draw)

    def init_stage(self):
        self.counter = 0
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0
        self.my_pos = [8*8,8*12]
        self.my_dir = 0
        self.mons = [[8*7,8*8]]
        self.mons_dir = [4]
        self.mons_active = [True]
        self.power_count = 0  # パワーエサ用
        self.power_add_count = 0  # 齧ったの何匹目？
        self.power_add_SCORE = [100]
        self.power_add_pos = []
        self.eat_cnt = 0
        self.is_clear = False
        self.init_tilemap()

    def init_tilemap(self):
        for y in range(16):
            for x in range(16):
                if pyxel.tilemaps[0].pget(x,y) == (2,0):
                    pyxel.tilemaps[0].pset(x,y,(0,1))
                elif pyxel.tilemaps[0].pget(x,y) == (3,0):
                    pyxel.tilemaps[0].pset(x,y,(1,1))

    def update(self):
        ### 独自のframeカウンター
        self.counter += 1
        
        ### バトル中なら
        if self.in_battle:
            self.update_battle()
            return

        ### ステージクリアしていたら
        if self.is_clear:
            return

        ### ステージクリアしたかの確認
        if self.eat_cnt > 117 or pyxel.btnp(pyxel.KEY_0):
            self.is_clear = True
            self.is_gaming = False
            self.counter = 0

        ### 自分と敵の当たり判定 　※バトル開始
        for i in range(1):
            dx = abs(self.my_pos[0] - self.mons[i][0])
            dy = abs(self.my_pos[1] - self.mons[i][1])
            if dx < 6 and dy < 6:
                if self.power_count > 0: # パワークッキー中に敵と接触
                    if self.mons_active[i]:
                        self.score += self.power_add_SCORE[self.power_add_count] # 加点処理
                        self.power_add_pos.append([self.mons[i][0],self.mons[i][1]])
                        self.power_add_count += 1
                        self.mons[i] = [8*(8-(i%2)),8*8]
                        self.mons_active[i] = False
                else: # パワークッキー中じゃなくて敵と接触したら
                    self.start_battle() # バトル開始

        ### 敵キャラの移動
        for i in range(1):
            if self.mons_active[i]: ## モンスターがアクティブで、
                if self.mons[i][0]%8==0 and self.mons[i][1]%8==0: #マス目上
                    self.teki_change_move(i)
                else: #マスの間を移動中
                    self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                    self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)

        ### ゲームオーバーしていたら
        if not self.is_gaming:
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.is_gaming = True
                self.init_stage()
            return

        ### パワークッキーのカウントダウン
        if self.power_count > 0:
            self.power_count -= 1
            if self.power_count <= 0:
                self.mons_active = [True]
                self.power_add_count = 0
                self.power_add_pos = []
                self.counter = 0


        ### 自キャラの移動とクッキー食べる処理
        if self.my_pos[0]%8==0 and self.my_pos[1]%8==0:
            cx = int(self.my_pos[0]/8)
            cy = int(self.my_pos[1]/8)
            
            tmp_dir = self.my_dir
            for i in range(4):
                if pyxel.btn(self.KEY[i]) or pyxel.btn(self.GPAD[i]):
                    tmp_dir = i + 1
            
            tmpnx = cx + self.D[tmp_dir][0]
            tmpny = cy + self.D[tmp_dir][1]
            tmptpl = pyxel.tilemaps[0].pget(tmpnx,tmpny)
            if tmp_dir != 0 and tmptpl == (1,0): # 向きを変えようとしたけど壁だった
                nx = cx + self.D[self.my_dir][0]
                ny = cy + self.D[self.my_dir][1]
                tpl = pyxel.tilemaps[0].pget(nx,ny)
                if tpl == (1,0): # さらに今の方向も壁だったならば
                    self.my_dir = 0 # 停止せよ、壁以外だったらそのまま進みなさい
                self.my_pos[0] += (self.D[self.my_dir][0] * 2)
                self.my_pos[1] += (self.D[self.my_dir][1] * 2)
            else:
                self.my_dir = tmp_dir
                nx = cx + self.D[self.my_dir][0]
                ny = cy + self.D[self.my_dir][1]
                tpl = pyxel.tilemaps[0].pget(nx,ny)
                if tpl == (1,0): # 進行方向が壁だったら
                    self.my_dir = 0 # 停止
                if tpl == (0,1): # 進行方向がクッキーだったら
                    self.score += 1 # 1点追加
                    self.eat_cnt += 1 #食べた数を1増やす
                    pyxel.tilemaps[0].pset(nx,ny,(2,0)) # 通路に変える
                elif tpl == (1,1): # 進行方向がパワークッキーだったら
                    self.score += 5 # 5点追加
                    self.eat_cnt += 1 #食べた数を1増やす
                    self.power_count = 120 # パワーアップ中にする
                    pyxel.tilemaps[0].pset(nx,ny,(3,0)) # 通路に変える
                    self.power_add_count = 0
                    self.power_add_pos = []
                    self.mons_active = [True]

                self.my_pos[0] += (self.D[self.my_dir][0] * 2)
                self.my_pos[1] += (self.D[self.my_dir][1] * 2)
        else:
            self.my_pos[0] += (self.D[self.my_dir][0] * 2)
            self.my_pos[1] += (self.D[self.my_dir][1] * 2)


    def draw_stage_clear_demo(self):
        if self.counter < 24:
            pyxel.circ(self.my_pos[0],self.my_pos[1],self.counter*4,self.counter%16)
        elif self.counter < 48:
            pyxel.cls(0)
        elif self.counter == 48:
            self.p_x = 128
            self.m_x = 153
        elif self.counter < 220:
            pyxel.cls(0)
            pyxel.blt(self.p_x,56,0,self.counter%2*8,40,8,8,0)
            pyxel.blt(self.m_x,56,0,8,48,8,8,0)
            self.p_x -= 0.9
            self.m_x -= 1
        elif self.counter == 220:
            self.p_x = -150
            self.m_x = -8
        elif self.counter < 440:
            pyxel.cls(0)
            pyxel.blt(self.m_x,56,0,0,80,8,8,0)
            pyxel.blt(self.p_x,48,0,self.counter%2*16,136,16,16,0)
            self.m_x += 1
            self.p_x += 1.7
        else:
            self.is_clear = False
            self.is_gaming = False
            self.counter = 0
            self.eat_cnt = 0

    def draw(self):
        ### バトル中ならバトル画面を描画
        if self.in_battle:
            self.draw_battle()
            return
            
        ### ステージクリアしていたらデモ画面（インターミッション）を表示します
        if self.is_clear:
            self.draw_stage_clear_demo()
            return

        ### 画面全体を黒塗り
        pyxel.cls(0)
        ### マップを描画
        pyxel.bltm(0,0,0,0,0,128,128)
        ### ハイスコアとスコアを表示
        pyxel.text(138, 8,"Hi-Score",13)
        pyxel.text(138,16,"{}".format(self.high_score).rjust(8),7)
        pyxel.text(138,28,"   Score",13)
        pyxel.text(138,36,"{}".format(self.score).rjust(8),7)
        # 敵キャラ紹介
        pyxel.text(138, 54,"MATIBUSE",13)
        pyxel.blt(162,60,0,0,56,8,8,0)
        ### 敵キャラを描画
        for i,m in enumerate(self.mons):
            if self.power_count > 0:  #パワークッキー中
                if self.power_count > 48:
                    pyxel.blt(m[0],m[1],0,0,80,8,8,0)
                else:
                    pyxel.blt(m[0],m[1],0,pyxel.frame_count%6*8,80,8,8,0)
            elif self.mons_dir[i] > 2: # 左向き
                pyxel.blt(m[0],m[1],0,8,56,8,8,0)
            else: # 右向き
                pyxel.blt(m[0],m[1],0,0,56,8,8,0)
        ### ゲームオーバーならメッセージを描画してreturn
        if not self.is_gaming:
            pyxel.text(48,56,"GAME OVER",pyxel.frame_count%16)
            pyxel.text(24,72,"PRESS BUTTON TO RESTART",pyxel.frame_count%16)
            return
        ### 自キャラを描画
        if self.my_dir == 0:
            pyxel.blt(self.my_pos[0],self.my_pos[1],0,0,16,8,8,0)
        else:
            pyxel.blt(self.my_pos[0],self.my_pos[1],0,(pyxel.frame_count%2)*8,8+self.my_dir*8,8,8,0)
            pyxel.play(0,0)

        ### 敵がイジケ中なら点数表示
        if self.power_count > 0:
            for i,lst in enumerate(self.power_add_pos):
                pyxel.blt(lst[0],lst[1],0,i*16,88,16,8,0)

    def teki_change_move(self,i):
        ###### 目標地点（tx, ty）を求める 
        ### ピンク（まちぶせ）
        if (self.counter % 750) < 150:  # 縄張りに移動
            tx = (  2  + pyxel.rndi(-2,2) ) * 8
            ty = (  2  + pyxel.rndi(-2,2) ) * 8
        else: # 自キャラの数歩先を目標地点にする
            tx = self.my_pos[0] + (self.D[self.my_dir][0] * 24)
            ty = self.my_pos[1] + (self.D[self.my_dir][1] * 24)

        ###### 目標地点（tx,ty）に向けて移動を行う        
        self.mons_walk(i, tx, ty)

    def mons_walk(self, i, tx, ty):
        newdir = 4
        if self.mons_dir[i] != 2:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if tx < self.mons[i][0] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        newdir = 2
        if self.mons_dir[i] != 4:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if tx > self.mons[i][0] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        newdir = 1
        if self.mons_dir[i] != 3:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if ty < self.mons[i][1] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        newdir = 3
        if self.mons_dir[i] != 1:
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if ty > self.mons[i][1] and tpl != (1,0):
                self.mons_dir[i] = newdir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

        ### 止まらないよ！
        while True:
            dir = pyxel.rndi(1,4)
            nx = int(self.mons[i][0]/8) + self.D[dir][0]
            ny = int(self.mons[i][1]/8) + self.D[dir][1]
            tpl = pyxel.tilemaps[0].pget(nx,ny)
            if tpl != (1,0):
                self.mons_dir[i] = dir
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)
                return

    def start_battle(self):
        self.in_battle = True
        self.battle_step = 0
        self.battle_counter = 0
        self.player_hp = 20
        self.enemy_hp = 10
        self.battle_text = "A WILD GHOST APPEARED!"
        self.selected_option = 0
    
    def update_battle(self):
        self.battle_counter += 1
        
        # イントロアニメーション
        if self.battle_step == 0:
            if self.battle_counter > 60:
                self.battle_step = 1
                self.battle_text = "WHAT WILL YOU DO?"
                
        # プレイヤーの選択
        elif self.battle_step == 1:
            # 上下キーで選択
            if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(self.GPAD[0]):
                self.selected_option = (self.selected_option - 1) % len(self.battle_options)
            if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(self.GPAD[2]):
                self.selected_option = (self.selected_option + 1) % len(self.battle_options)
            
            # 決定
            if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                if self.battle_options[self.selected_option] == "ATTACK":
                    # 攻撃選択
                    damage = pyxel.rndi(3, 8)
                    self.enemy_hp -= damage
                    self.battle_text = f"YOU DID {damage} DAMAGE!"
                    self.battle_step = 2
                    self.battle_counter = 0
                elif self.battle_options[self.selected_option] == "MAGIC":
                    # 魔法選択
                    damage = pyxel.rndi(5, 12)
                    self.enemy_hp -= damage
                    self.battle_text = f"MAGIC BLAST! {damage} DAMAGE!"
                    self.battle_step = 2
                    self.battle_counter = 0
                elif self.battle_options[self.selected_option] == "RUN":
                    # 逃げる選択
                    if pyxel.rndi(0, 10) > 3:
                        self.battle_text = "GOT AWAY SAFELY!"
                        self.battle_step = 4
                    else:
                        self.battle_text = "COULDN'T ESCAPE!"
                        self.battle_step = 2
                    self.battle_counter = 0
        
        # 敵の行動
        elif self.battle_step == 2:
            if self.battle_counter > 45:
                if self.enemy_hp <= 0:
                    self.battle_text = "YOU DEFEATED THE GHOST!"
                    self.score += 50  # 勝利ボーナス
                    self.battle_step = 4
                    self.battle_counter = 0
                else:
                    self.battle_step = 3
                    damage = pyxel.rndi(2, 6)
                    self.player_hp -= damage
                    self.battle_text = f"GHOST ATTACKED! {damage} DAMAGE!"
                    self.battle_counter = 0
        
        # 敵の行動後
        elif self.battle_step == 3:
            if self.battle_counter > 45:
                if self.player_hp <= 0:
                    self.battle_text = "YOU WERE DEFEATED!"
                    self.battle_step = 4
                else:
                    self.battle_step = 1
                    self.battle_text = "WHAT WILL YOU DO?"
        
        # バトル終了
        elif self.battle_step == 4:
            if self.battle_counter > 60:
                self.in_battle = False
                if self.player_hp <= 0:
                    self.is_gaming = False  # ゲームオーバー
                else:
                    # 敵を少し遠くに移動させる
                    self.mons[0][0] = pyxel.rndi(0, 15) * 8
                    self.mons[0][1] = pyxel.rndi(0, 15) * 8
    
    def draw_battle(self):
        pyxel.cls(0)
        
        # バトル背景
        for y in range(16):
            col = 5 if y % 2 == 0 else 1
            pyxel.rect(0, y * 8, 180, 8, col)
        
        # 敵表示
        if self.battle_step < 4 or self.enemy_hp > 0:
            enemy_x = 90
            enemy_y = 40
            enemy_scale = 3
            
            # 敵のアニメーション
            bounce = abs(pyxel.sin(self.battle_counter * 0.1)) * 5
            
            # ゴーストの描画（大きく）
            pyxel.blt(enemy_x - 12, enemy_y - 12 + bounce, 0, 0, 56, 8 * enemy_scale, 8 * enemy_scale, 0)
        
        # UI枠
        pyxel.rectb(0, 90, 180, 38, 7)
        pyxel.rect(1, 91, 178, 36, 0)
        
        # テキスト表示
        pyxel.text(10, 96, self.battle_text, 7)
        
        # HP表示
        pyxel.text(10, 106, f"YOUR HP: {self.player_hp}", 11)
        if self.enemy_hp > 0:
            pyxel.text(100, 106, f"GHOST HP: {self.enemy_hp}", 8)
        
        # 選択肢表示
        if self.battle_step == 1:
            for i, option in enumerate(self.battle_options):
                color = 10 if i == self.selected_option else 7
                pyxel.text(10, 116 + i * 8, option, color)
                if i == self.selected_option:
                    pyxel.text(5, 116 + i * 8, ">", 10)

App()
