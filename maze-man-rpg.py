#       .--.
#   .-"     "-.
#  /  o     o  \
# |            |   < CHOMP!
# |  \     /  |
# \  '---'  /
#  '-.___.-'   > MAZE MAN RPG
#
# By Eli & Son

# This imports the game engine we are using
import pyxel

# This function runs when the game starts - it sets up everything we need
class App():
    def __init__(self):
        pyxel.init(180,128,title="Maze Man RPG",fps=24) # Makes a window
        pyxel.load("maze-man-rpg.pyxres") # Loads our game's pictures and sounds
        self.is_gaming = True # This means the game is running
        self.in_battle = False # This is False when we're not fighting a ghost
        self.battle_step = 0 # Keeps track of what's happening in a battle
        self.battle_counter = 0 # Counts time during battles
        self.player_hp = 10 # Your health points (HP) - when this reaches 0, it's game over!
        self.enemy_hp = 10 # The ghost's health points
        self.battle_text = "" # Text that shows during battles
        self.battle_options = ["ATTACK", "MAGIC", "RUN"] # Things you can do in a battle
        self.selected_option = 0 # Which battle option is selected (0 is the first one)
        self.KEY = [pyxel.KEY_UP,pyxel.KEY_RIGHT,pyxel.KEY_DOWN,pyxel.KEY_LEFT] # Arrow keys on keyboard
        self.GPAD = [
                     pyxel.GAMEPAD1_BUTTON_DPAD_UP,    # Up on gamepad
                     pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, # Right on gamepad
                     pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,  # Down on gamepad
                     pyxel.GAMEPAD1_BUTTON_DPAD_LEFT   # Left on gamepad
        ]
        # D stands for Direction - this list helps the game know which way to move:
        # [0,0] = don't move, [0,-1] = up, [1,0] = right, [0,1] = down, [-1,0] = left
        self.D = [[0,0],[0,-1],[1,0],[0,1],[-1,0]]
        self.high_score = 0  # The best score you've gotten so far
        self.score = 0  # Your current score
        self.init_stage()  # Sets up the maze and characters
        pyxel.run(self.update,self.draw)  # Starts the game and keeps it updated!

    # This function sets up a new maze level
    def init_stage(self):
        self.counter = 0 # Counts time (frames) in the game
        if self.score > self.high_score:
            self.high_score = self.score # Update high score if you got a new best score
        self.score = 0 # Reset score for the new level
        self.my_pos = [8*8,8*12] # Your starting position (x,y) on the screen
        self.my_dir = 0 # Which way you're facing (0 = stopped)
        self.mons = [[8*7,8*8]] # Ghost positions [x,y]
        self.mons_dir = [4] # Which way ghosts are moving (4 = left)
        self.mons_active = [True] # If True, ghosts can move around
        self.power_count = 0 # Power pellet timer - when > 0, you can eat ghosts!
        self.power_add_count = 0 # Keeps track of how many ghosts you've eaten
        self.power_add_SCORE = [100] # Points for eating ghosts
        self.power_add_pos = [] # Positions where you've eaten ghosts
        self.eat_cnt = 0 # How many pellets you've eaten
        self.is_clear = False # True when you've cleared the level
        self.init_tilemap() # Set up the maze

    def init_tilemap(self):
        # This function resets the dots in the maze
        for y in range(16):
            for x in range(16):
                if pyxel.tilemaps[0].pget(x,y) == (2,0):
                    pyxel.tilemaps[0].pset(x,y,(0,1))  # Places regular pellets
                elif pyxel.tilemaps[0].pget(x,y) == (3,0):
                    pyxel.tilemaps[0].pset(x,y,(1,1))  # Places power pellets

    def update(self):
        # This is the main game function that runs every frame
        # It checks for button presses and updates everything in the game
        
        # Add 1 to our timer each frame
        self.counter += 1
        
        # If we're in a battle, do battle stuff instead
        if self.in_battle:
            self.update_battle()
            return

        # If we've cleared the level, don't do anything else
        if self.is_clear:
            return

        # Check if we've cleared the level (by eating all pellets or pressing 0)
        if self.eat_cnt > 117 or pyxel.btnp(pyxel.KEY_0):
            self.is_clear = True
            self.is_gaming = False
            self.counter = 0

        # Check if you've bumped into a ghost
        for i in range(1):
            dx = abs(self.my_pos[0] - self.mons[i][0])  # Distance between you and ghost (x direction)
            dy = abs(self.my_pos[1] - self.mons[i][1])  # Distance between you and ghost (y direction)
            if dx < 6 and dy < 6:  # If you're very close to a ghost...
                if self.power_count > 0:  # If you've eaten a power pellet
                    # You can eat the ghost!
                    if self.mons_active[i]:
                        self.score += self.power_add_SCORE[self.power_add_count]  # Add points
                        self.power_add_pos.append([self.mons[i][0],self.mons[i][1]])
                        self.power_add_count += 1
                        self.mons[i] = [8*(8-(i%2)),8*8]  # Send ghost back to start
                        self.mons_active[i] = False  # Ghost can't move for a bit
                else:  # If you don't have a power pellet
                    # Start a battle with the ghost!
                    self.start_battle()

        # Move the ghosts
        for i in range(1):
            if self.mons_active[i]:  # If the ghost can move
                if self.mons[i][0]%8==0 and self.mons[i][1]%8==0:  # If ghost is on a grid point
                    self.teki_change_move(i)  # Choose a new direction
                else:  # If ghost is between grid points
                    # Keep moving in the current direction
                    self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)
                    self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)

        # If game over, check for restart button
        if not self.is_gaming:
            if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
                self.is_gaming = True
                self.init_stage()
            return

        # Count down the power pellet timer
        if self.power_count > 0:
            self.power_count -= 1
            if self.power_count <= 0:  # When power runs out
                self.mons_active = [True]  # Ghosts start moving again
                self.power_add_count = 0
                self.power_add_pos = []
                self.counter = 0

        # Move the player and check if they eat pellets
        if self.my_pos[0]%8==0 and self.my_pos[1]%8==0:  # If player is on a grid point
            cx = int(self.my_pos[0]/8)  # Get grid x position
            cy = int(self.my_pos[1]/8)  # Get grid y position
            
            tmp_dir = self.my_dir  # Remember current direction
            for i in range(4):  # Check if arrow keys are pressed
                if pyxel.btn(self.KEY[i]) or pyxel.btn(self.GPAD[i]):
                    tmp_dir = i + 1  # Change direction if an arrow key is pressed
            
            tmpnx = cx + self.D[tmp_dir][0]  # Position if we move in the new direction (x)
            tmpny = cy + self.D[tmp_dir][1]  # Position if we move in the new direction (y)
            tmptpl = pyxel.tilemaps[0].pget(tmpnx,tmpny)  # What's at that new position?
            if tmp_dir != 0 and tmptpl == (1,0):  # If you tried to change direction but hit a wall
                # Try continuing in the original direction
                nx = cx + self.D[self.my_dir][0]
                ny = cy + self.D[self.my_dir][1]
                tpl = pyxel.tilemaps[0].pget(nx,ny)
                if tpl == (1,0):  # If the original direction has a wall too
                    self.my_dir = 0  # Stop moving
                self.my_pos[0] += (self.D[self.my_dir][0] * 2)  # Move in original direction
                self.my_pos[1] += (self.D[self.my_dir][1] * 2)  # Move in original direction
            else:  # If the new direction is good (no wall)
                self.my_dir = tmp_dir  # Change to the new direction
                nx = cx + self.D[self.my_dir][0]  # Position ahead in new direction (x)
                ny = cy + self.D[self.my_dir][1]  # Position ahead in new direction (y)
                tpl = pyxel.tilemaps[0].pget(nx,ny)  # What's ahead of us?
                if tpl == (1,0):  # If there's a wall ahead
                    self.my_dir = 0  # Stop moving
                if tpl == (0,1):  # If there's a regular pellet ahead
                    self.score += 1  # Add 1 point to your score
                    self.eat_cnt += 1  # Count this pellet as eaten
                    pyxel.tilemaps[0].pset(nx,ny,(2,0))  # Remove the pellet from the maze
                elif tpl == (1,1):  # If there's a power pellet ahead
                    self.score += 5  # Add 5 points to your score
                    self.eat_cnt += 1  # Count this pellet as eaten
                    self.power_count = 120  # Turn on power mode for 120 frames (5 seconds)
                    pyxel.tilemaps[0].pset(nx,ny,(3,0))  # Remove the power pellet from the maze
                    self.power_add_count = 0
                    self.power_add_pos = []
                    self.mons_active = [True]  # Make sure ghosts are active

                # Move in the new direction
                self.my_pos[0] += (self.D[self.my_dir][0] * 2)
                self.my_pos[1] += (self.D[self.my_dir][1] * 2)
        else:  # If player is between grid points
            # Keep moving in the current direction
            self.my_pos[0] += (self.D[self.my_dir][0] * 2)
            self.my_pos[1] += (self.D[self.my_dir][1] * 2)

    def draw_stage_clear_demo(self):
        # This function shows a fun animation when you clear a level
        
        # First part: Draw an expanding circle 
        if self.counter < 24:
            pyxel.circ(self.my_pos[0],self.my_pos[1],self.counter*4,self.counter%16)
        # Clear the screen for a moment
        elif self.counter < 48:
            pyxel.cls(0)
        # Set up positions for the next animation
        elif self.counter == 48:
            self.p_x = 128  # Player starts at right side
            self.m_x = 153  # Monster starts further right
        # First chase scene: Player running left, monster chasing
        elif self.counter < 220:
            pyxel.cls(0)
            pyxel.blt(self.p_x,56,0,self.counter%2*8,40,8,8,0)  # Draw player (alternating frames)
            pyxel.blt(self.m_x,56,0,8,48,8,8,0)  # Draw monster
            self.p_x -= 0.9  # Move player left
            self.m_x -= 1  # Move monster left (slightly faster)
        # Set up positions for second chase scene
        elif self.counter == 220:
            self.p_x = -150  # Player starts far off left
            self.m_x = -8    # Monster starts at left edge
        # Second chase scene: Giant player chasing scared monster!
        elif self.counter < 440:
            pyxel.cls(0)
            pyxel.blt(self.m_x,56,0,0,80,8,8,0)  # Draw scared monster
            pyxel.blt(self.p_x,48,0,self.counter%2*16,136,16,16,0)  # Draw giant player
            self.m_x += 1  # Move monster right
            self.p_x += 1.7  # Move player right (faster)
        # End of animation, prepare for next level
        else:
            self.is_clear = False
            self.is_gaming = False
            self.counter = 0
            self.eat_cnt = 0

    def draw(self):
        ### バトル中ならバトル画面を描画
        # If in battle, draw battle screen
        if self.in_battle:
            self.draw_battle()
            return
            
        ### ステージクリアしていたらデモ画面（インターミッション）を表示します
        # If stage is cleared, show demo screen (intermission)
        if self.is_clear:
            self.draw_stage_clear_demo()
            return

        ### 画面全体を黒塗り
        # Fill the screen black
        pyxel.cls(0)
        ### マップを描画
        # Draw the map
        pyxel.bltm(0,0,0,0,0,128,128)
        ### ハイスコアとスコアを表示
        # Display high score and score
        pyxel.text(143, 8,"Hi-Score",13)  # Adjusted for 204 width
        pyxel.text(143,16,"{}".format(self.high_score).rjust(8),7)
        pyxel.text(143,28,"   Score",13)  # Adjusted for 204 width
        pyxel.text(143,36,"{}".format(self.score).rjust(8),7)
        # 敵キャラ紹介
        # Enemy character introduction
        pyxel.text(139, 54,"    BUNNY",13)  # Moved 4px left from previous position
        pyxel.blt(167,60,0,0,56,8,8,0)  # Moved 4px left from previous position
        ### 敵キャラを描画
        # Draw enemy characters
        for i,m in enumerate(self.mons):
            if self.power_count > 0:  #パワークッキー中
                # During power cookie effect
                if self.power_count > 48:
                    pyxel.blt(m[0],m[1],0,0,80,8,8,0)
                else:
                    pyxel.blt(m[0],m[1],0,pyxel.frame_count%6*8,80,8,8,0)
            elif self.mons_dir[i] > 2: # 左向き
                # Facing left
                pyxel.blt(m[0],m[1],0,8,56,8,8,0)
            else: # 右向き
                # Facing right
                pyxel.blt(m[0],m[1],0,0,56,8,8,0)
        ### ゲームオーバーならメッセージを描画してreturn
        # If game over, draw message and return
        if not self.is_gaming:
            pyxel.text(48,56,"GAME OVER",pyxel.frame_count%16)
            pyxel.text(24,72,"PRESS BUTTON TO RESTART",pyxel.frame_count%16)
            return
        ### 自キャラを描画
        # Draw player character
        if self.my_dir == 0:
            pyxel.blt(self.my_pos[0],self.my_pos[1],0,0,16,8,8,0)
        else:
            pyxel.blt(self.my_pos[0],self.my_pos[1],0,(pyxel.frame_count%2)*8,8+self.my_dir*8,8,8,0)
            pyxel.play(0,0)

        ### 敵がイジケ中なら点数表示
        # Display score if ghosts are vulnerable
        if self.power_count > 0:
            for i,lst in enumerate(self.power_add_pos):
                pyxel.blt(lst[0],lst[1],0,i*16,88,16,8,0)

    def teki_change_move(self,i):
        # This function decides where the ghost should try to go
        
        # Sometimes ghosts stay in their territory, sometimes they chase you
        if (self.counter % 750) < 150:  # About 20% of the time, stay in home area
            # Pick a random spot in the top-left corner (their territory)
            tx = (  2  + pyxel.rndi(-2,2) ) * 8
            ty = (  2  + pyxel.rndi(-2,2) ) * 8
        else:  # About 80% of the time, chase the player
            # Try to get to a spot ahead of where the player is going
            tx = self.my_pos[0] + (self.D[self.my_dir][0] * 24)
            ty = self.my_pos[1] + (self.D[self.my_dir][1] * 24)

        # Try to move toward the target position
        self.mons_walk(i, tx, ty)

    def mons_walk(self, i, tx, ty):
        # This function makes ghosts try to move toward their target
        # It checks different directions in order: left, right, up, down
        
        # Try moving left
        newdir = 4  # 4 means left
        if self.mons_dir[i] != 2:  # If not already moving right (don't turn around)
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]  # Position if we go left
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]  # Position if we go left
            tpl = pyxel.tilemaps[0].pget(nx,ny)  # What's to the left?
            if tx < self.mons[i][0] and tpl != (1,0):  # If target is left and no wall
                self.mons_dir[i] = newdir  # Go left
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)  # Move left
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)  # Move left
                return

        # Try moving right
        newdir = 2  # 2 means right
        if self.mons_dir[i] != 4:  # If not already moving left (don't turn around)
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]  # Position if we go right
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]  # Position if we go right
            tpl = pyxel.tilemaps[0].pget(nx,ny)  # What's to the right?
            if tx > self.mons[i][0] and tpl != (1,0):  # If target is right and no wall
                self.mons_dir[i] = newdir  # Go right
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)  # Move right
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)  # Move right
                return

        # Try moving up
        newdir = 1  # 1 means up
        if self.mons_dir[i] != 3:  # If not already moving down (don't turn around)
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]  # Position if we go up
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]  # Position if we go up
            tpl = pyxel.tilemaps[0].pget(nx,ny)  # What's above?
            if ty < self.mons[i][1] and tpl != (1,0):  # If target is above and no wall
                self.mons_dir[i] = newdir  # Go up
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)  # Move up
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)  # Move up
                return

        # Try moving down
        newdir = 3  # 3 means down
        if self.mons_dir[i] != 1:  # If not already moving up (don't turn around)
            nx = int(self.mons[i][0]/8) + self.D[newdir][0]  # Position if we go down
            ny = int(self.mons[i][1]/8) + self.D[newdir][1]  # Position if we go down
            tpl = pyxel.tilemaps[0].pget(nx,ny)  # What's below?
            if ty > self.mons[i][1] and tpl != (1,0):  # If target is below and no wall
                self.mons_dir[i] = newdir  # Go down
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)  # Move down
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)  # Move down
                return

        # If we can't move in any good direction, pick a random direction
        # This makes sure ghosts don't get stuck
        while True:
            dir = pyxel.rndi(1,4)  # Pick a random direction (1-4)
            nx = int(self.mons[i][0]/8) + self.D[dir][0]  # Position if we go that way
            ny = int(self.mons[i][1]/8) + self.D[dir][1]  # Position if we go that way
            tpl = pyxel.tilemaps[0].pget(nx,ny)  # What's in that direction?
            if tpl != (1,0):  # If no wall in that direction
                self.mons_dir[i] = dir  # Go that way
                self.mons[i][0] += (self.D[self.mons_dir[i]][0] * 1)  # Move that way
                self.mons[i][1] += (self.D[self.mons_dir[i]][1] * 1)  # Move that way
                return

    def start_battle(self):
        # This function starts a battle when you touch a ghost
        self.in_battle = True  # Turn on battle mode
        self.battle_step = 0  # Start at first step of battle
        self.battle_counter = 0  # Reset battle timer
        self.player_hp = 20  # Reset your health points
        self.enemy_hp = 10  # Reset ghost health points
        self.battle_text = "A WILD GHOST APPEARED!"  # First message to show
        self.selected_option = 0  # Select first action (ATTACK)
    
    def update_battle(self):
        # This function updates the battle each frame
        self.battle_counter += 1  # Increase battle timer
        
        # Step 0: Show intro message
        if self.battle_step == 0:
            if self.battle_counter > 60:  # After 60 frames (2.5 seconds)
                self.battle_step = 1  # Move to next step
                self.battle_text = "WHAT WILL YOU DO?"  # Ask player to choose
                
        # Step 1: Player selects an action
        elif self.battle_step == 1:
            # Move selection up/down with arrow keys
            if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(self.GPAD[0]):
                self.selected_option = (self.selected_option - 1) % len(self.battle_options)  # Go up one option
            if pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(self.GPAD[2]):
                self.selected_option = (self.selected_option + 1) % len(self.battle_options)  # Go down one option
            
            # Press any of these keys to confirm your choice
            if (pyxel.btnp(pyxel.KEY_Z) or 
                pyxel.btnp(pyxel.KEY_SPACE) or 
                pyxel.btnp(pyxel.KEY_RETURN) or 
                pyxel.btnp(pyxel.KEY_X) or 
                pyxel.btnp(pyxel.KEY_A) or 
                pyxel.btnp(pyxel.KEY_S) or 
                pyxel.btnp(pyxel.KEY_D) or 
                pyxel.btnp(pyxel.KEY_Q) or 
                pyxel.btnp(pyxel.KEY_W) or 
                pyxel.btnp(pyxel.KEY_E) or 
                pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)):
                
                # Do the selected action
                self._execute_battle_option()
        
        # Step 2: Enemy's turn
        elif self.battle_step == 2:
            if self.battle_counter > 45:  # After 45 frames (almost 2 seconds)
                if self.enemy_hp <= 0:  # If ghost has no health left
                    self.battle_text = "YOU DEFEATED THE GHOST!"  # Show victory message
                    self.score += 50  # Add 50 points for winning
                    self.battle_step = 4  # Go to battle end step
                    self.battle_counter = 0  # Reset timer
                else:  # If ghost still has health
                    self.battle_step = 3  # Go to enemy attack step
                    damage = pyxel.rndi(2, 6)  # Random damage between 2-6
                    self.player_hp -= damage  # Reduce your health
                    self.battle_text = f"GHOST ATTACKED! {damage} DAMAGE!"  # Show attack message
                    self.battle_counter = 0  # Reset timer
        
        # Step 3: After enemy attack
        elif self.battle_step == 3:
            if self.battle_counter > 45:  # After 45 frames (almost 2 seconds)
                if self.player_hp <= 0:  # If you have no health left
                    self.battle_text = "YOU WERE DEFEATED!"  # Show defeat message
                    self.battle_step = 4  # Go to battle end step
                else:  # If you still have health
                    self.battle_step = 1  # Back to your turn
                    self.battle_text = "WHAT WILL YOU DO?"  # Ask for your next move
        
        # Step 4: Battle end
        elif self.battle_step == 4:
            if self.battle_counter > 60:  # After 60 frames (2.5 seconds)
                self.in_battle = False  # End battle mode
                if self.player_hp <= 0:  # If you lost
                    self.is_gaming = False  # Game over
                else:  # If you won
                    # Move the ghost to a random spot away from you
                    self.mons[0][0] = pyxel.rndi(0, 15) * 8
                    self.mons[0][1] = pyxel.rndi(0, 15) * 8
    
    def _execute_battle_option(self):
        # This function does different things based on your battle choice
        if self.battle_options[self.selected_option] == "ATTACK":
            # If you chose to ATTACK
            damage = pyxel.rndi(3, 8)  # Random damage between 3-8
            self.enemy_hp -= damage  # Reduce ghost's health
            self.battle_text = f"YOU DID {damage} DAMAGE!"  # Show damage message
            self.battle_step = 2  # Go to enemy's turn
            self.battle_counter = 0  # Reset timer
        elif self.battle_options[self.selected_option] == "MAGIC":
            # If you chose MAGIC
            damage = pyxel.rndi(5, 12)  # Random damage between 5-12 (stronger than attack)
            self.enemy_hp -= damage  # Reduce ghost's health
            self.battle_text = f"MAGIC BLAST! {damage} DAMAGE!"  # Show damage message
            self.battle_step = 2  # Go to enemy's turn
            self.battle_counter = 0  # Reset timer
        elif self.battle_options[self.selected_option] == "RUN":
            # If you chose RUN
            if pyxel.rndi(0, 10) > 3:  # 70% chance to escape
                self.battle_text = "GOT AWAY SAFELY!"  # Show escaped message
                self.battle_step = 4  # Go to battle end
            else:  # 30% chance to fail
                self.battle_text = "COULDN'T ESCAPE!"  # Show failed message
                self.battle_step = 2  # Go to enemy's turn
            self.battle_counter = 0  # Reset timer

    def draw_battle(self):
        # This function draws the battle screen
        pyxel.cls(0)  # Clear screen to black
        
        # Draw a cool wiggly background with green lines
        t = self.battle_counter * 2.5  # Animation speed
        
        # Draw four wavy lines that move differently
        for x in range(180):
            # First light green wave - this makes a wavy line that moves up and down
            wave1_y = int(15 + pyxel.sin(x * 2.0 + t) * 10)
            if 0 <= wave1_y < 70:  # Only draw if on screen
                pyxel.line(x, wave1_y, x, wave1_y, 11)  # Light green color
            
            # Second light green wave - another wavy line with different timing
            wave2_y = int(30 + pyxel.sin(x * 2.0 + t * 1.4 + 1.57) * 12)
            if 0 <= wave2_y < 70:
                pyxel.line(x, wave2_y, x, wave2_y, 11)  # Light green color
            
            # First dark green wave - darker wave with different timing
            wave3_y = int(45 + pyxel.sin(x * 2.0 + t * 0.8 + 3.14) * 10)
            if 0 <= wave3_y < 70:
                pyxel.line(x, wave3_y, x, wave3_y, 3)  # Dark green color
                
            # Second dark green wave - another dark wave
            wave4_y = int(60 + pyxel.sin(x * 2.0 + t * 1.2 + 4.71) * 8)
            if 0 <= wave4_y < 70:
                pyxel.line(x, wave4_y, x, wave4_y, 3)  # Dark green color
        
        # Draw the ghost (unless we've won the battle)
        if self.battle_step < 4 or self.enemy_hp > 0:
            enemy_x = 90  # Middle of screen
            enemy_y = 30  # Near top of screen
            
            # Make the ghost bounce up and down
            bounce = pyxel.sin(self.battle_counter * 0.1) * 3
            
            # Change ghost image every few frames to make it animate
            sprite_x = 0 if (self.battle_counter // 15) % 2 == 0 else 8
            
            # Draw the ghost with the bouncing effect
            pyxel.blt(enemy_x, enemy_y + bounce, 0, sprite_x, 56, 8, 8, 0)
        
        # Draw a black bar at the bottom for the UI
        pyxel.rect(0, 70, 180, 80, 0)
        
        # Show battle messages
        pyxel.text(10, 78, self.battle_text, 7)  # White text
        
        # Show health points
        pyxel.text(10, 88, f"YOUR HP: {self.player_hp}", 11)  # Green text for your HP
        if self.enemy_hp > 0:
            pyxel.text(100, 88, f"GHOST HP: {self.enemy_hp}", 8)  # Red text for ghost HP
        
        # Show battle options if it's your turn
        if self.battle_step == 1:
            for i, option in enumerate(self.battle_options):
                color = 10 if i == self.selected_option else 7  # Yellow for selected, white for others
                pyxel.text(10, 98 + i * 8, option, color)  # Draw each option
                if i == self.selected_option:
                    pyxel.text(5, 98 + i * 8, ">", 10)  # Draw a > symbol next to selected option

App()  # This starts the game!
