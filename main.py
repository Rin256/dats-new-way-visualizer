from math import pi, sin, cos
import json
import time

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core import TransparencyAttrib
from panda3d.core import WindowProperties
from panda3d.core import CollisionTraverser, CollisionNode, CollisionBox, CollisionRay, CollisionHandlerQueue
from direct.gui.OnscreenImage import OnscreenImage

loadPrcFile('settings.prc')

def degToRad(degrees):
    return degrees * (pi / 180.0)

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.selectedBlockType = 'snake'
        self.currentFrameIndex = 0
        
        self.showFences = True
        self.showFoods = True
        self.showSnakes = True
        self.showEnemies = True

        self.loadModels()
        self.setupLights()
        self.generateTerrain()
        self.setupCamera()
        self.setupSkybox()
        self.captureMouse()
        self.setupControls()

        taskMgr.add(self.update, 'update')

    def update(self, task):
        dt = globalClock.getDt()

        playerMoveSpeed = 100

        x_movement = 0
        y_movement = 0
        z_movement = 0

        if self.keyMap['forward']:
            x_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
        if self.keyMap['backward']:
            x_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
        if self.keyMap['left']:
            x_movement -= dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement -= dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        if self.keyMap['right']:
            x_movement += dt * playerMoveSpeed * cos(degToRad(camera.getH()))
            y_movement += dt * playerMoveSpeed * sin(degToRad(camera.getH()))
        if self.keyMap['up']:
            z_movement += dt * playerMoveSpeed
        if self.keyMap['down']:
            z_movement -= dt * playerMoveSpeed

        camera.setPos(
            camera.getX() + x_movement,
            camera.getY() + y_movement,
            camera.getZ() + z_movement,
        )

        if self.cameraSwingActivated:
            md = self.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()

            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY

            self.cameraSwingFactor = 10

            currentH = self.camera.getH()
            currentP = self.camera.getP()

            self.camera.setHpr(
                currentH - mouseChangeX * dt * self.cameraSwingFactor,
                min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                0
            )

            self.lastMouseX = mouseX
            self.lastMouseY = mouseY

        return task.cont

    def generateTerrain(self):
        # Load data dynamically based on the current frame index
        file_name = f'data/{self.currentFrameIndex}.json'
        try:
            with open(file_name, encoding='utf-8-sig') as file:
                data = json.load(file)
        except FileNotFoundError:
            print(f"No such file: {file_name}")
            return

        # Clear existing terrain blocks
        render.findAllMatches('new-block-placeholder').detach()

        if self.showFences:
            fences = data['fences']
            for fence in fences:
                self.createNewBlock(
                    fence[0] * 2 - 20,
                    fence[1] * 2 - 20,
                    fence[2] * 2,
                    'sand'
                )

        if self.showFoods:
            foods = data['food']
            for food in foods:
                foodBlock = food['c']
                self.createNewBlock(
                    foodBlock[0] * 2 - 20,
                    foodBlock[1] * 2 - 20,
                    foodBlock[2] * 2,
                    'food'
                )

        if self.showSnakes:
            snakes = data['snakes']
            for snake in snakes:
                if snake['status'] != 'alive':
                    continue

                for snakeBlock in snake['geometry']:
                    self.createNewBlock(
                        snakeBlock[0] * 2 - 20,
                        snakeBlock[1] * 2 - 20,
                        snakeBlock[2] * 2,
                        'snake'
                    )

        if self.showEnemies:
            enemies = data['enemies']
            for enemy in enemies:
                if enemy['status'] != 'alive':
                    continue

                for enemyBlock in enemy['geometry']:
                    self.createNewBlock(
                        enemyBlock[0] * 2 - 20,
                        enemyBlock[1] * 2 - 20,
                        enemyBlock[2] * 2,
                        'enemy'
                    )

    def nextFrame(self):
        self.currentFrameIndex += 1
        self.generateTerrain()

    def previousFrame(self):
        self.currentFrameIndex -= 1
        self.generateTerrain()

    def changeShowFences(self):
        self.showFences = not self.showFences
        self.generateTerrain()

    def changeShowFoods(self):
        self.showFoods = not self.showFoods
        self.generateTerrain()

    def changeShowSnakes(self):
        self.showSnakes = not self.showSnakes
        self.generateTerrain()

    def changeShowEnemies(self):
        self.showEnemies = not self.showEnemies
        self.generateTerrain()

    def createNewBlock(self, x, y, z, type):
        newBlockNode = render.attachNewNode('new-block-placeholder')
        newBlockNode.setPos(x, y, z)

        if type == 'snake':
            self.snakeBlock.instanceTo(newBlockNode)
        elif type == 'enemy':
            self.enemyBlock.instanceTo(newBlockNode)
        elif type == 'sand':
            self.sandBlock.instanceTo(newBlockNode)
        elif type == 'food':
            self.foodBlock.instanceTo(newBlockNode)

        blockSolid = CollisionBox((-1, -1, -1), (1, 1, 1))
        blockNode = CollisionNode('block-collision-node')
        blockNode.addSolid(blockSolid)
        collider = newBlockNode.attachNewNode(blockNode)
        collider.setPythonTag('owner', newBlockNode)

    def loadModels(self):
        self.snakeBlock = loader.loadModel('snake-block.glb')
        self.enemyBlock = loader.loadModel('enemy-block.glb')
        self.foodBlock = loader.loadModel('food-block.glb')
        self.sandBlock = loader.loadModel('sand-block.glb')

    def setupLights(self):
        mainLight = DirectionalLight('main light')
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(30, -60, 0)
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)

    def setupControls(self):
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        self.accept('escape', self.releaseMouse)
        self.accept('mouse1', self.handleLeftClick)
        self.accept('mouse3', self.placeBlock)

        self.accept('w', self.updateKeyMap, ['forward', True])
        self.accept('w-up', self.updateKeyMap, ['forward', False])
        self.accept('a', self.updateKeyMap, ['left', True])
        self.accept('a-up', self.updateKeyMap, ['left', False])
        self.accept('s', self.updateKeyMap, ['backward', True])
        self.accept('s-up', self.updateKeyMap, ['backward', False])
        self.accept('d', self.updateKeyMap, ['right', True])
        self.accept('d-up', self.updateKeyMap, ['right', False])
        self.accept('space', self.updateKeyMap, ['up', True])
        self.accept('space-up', self.updateKeyMap, ['up', False])
        self.accept('lshift', self.updateKeyMap, ['down', True])
        self.accept('lshift-up', self.updateKeyMap, ['down', False])

        self.accept('1', self.setSelectedBlockType, ['snake'])
        self.accept('2', self.setSelectedBlockType, ['enemy'])
        self.accept('3', self.setSelectedBlockType, ['sand'])
        self.accept('4', self.setSelectedBlockType, ['food'])

        self.accept('+', self.nextFrame)
        self.accept('-', self.previousFrame)

        self.accept('1', self.changeShowFences)
        self.accept('2', self.changeShowFoods)
        self.accept('3', self.changeShowSnakes)
        self.accept('4', self.changeShowEnemies)

    def setSelectedBlockType(self, type):
        self.selectedBlockType = type

    def handleLeftClick(self):
        self.captureMouse()
        self.removeBlock()

    def removeBlock(self):
        if self.rayQueue.getNumEntries() > 0:
            self.rayQueue.sortEntries()
            rayHit = self.rayQueue.getEntry(0)

            hitNodePath = rayHit.getIntoNodePath()
            hitObject = hitNodePath.getPythonTag('owner')
            distanceFromPlayer = hitObject.getDistance(self.camera)

            if distanceFromPlayer < 12:
                hitNodePath.clearPythonTag('owner')
                hitObject.removeNode()

    def placeBlock(self):
        if self.rayQueue.getNumEntries() > 0:
            self.rayQueue.sortEntries()
            rayHit = self.rayQueue.getEntry(0)
            hitNodePath = rayHit.getIntoNodePath()
            normal = rayHit.getSurfaceNormal(hitNodePath)
            hitObject = hitNodePath.getPythonTag('owner')
            distanceFromPlayer = hitObject.getDistance(self.camera)

            if distanceFromPlayer < 14:
                hitBlockPos = hitObject.getPos()
                newBlockPos = hitBlockPos + normal * 2
                self.createNewBlock(newBlockPos.x, newBlockPos.y, newBlockPos.z, self.selectedBlockType)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def captureMouse(self):
        self.cameraSwingActivated = True

        md = self.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()

        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

    def releaseMouse(self):
        self.cameraSwingActivated = False

        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def setupCamera(self):
        self.disableMouse()
        self.camera.setPos(0, 0, 3)
        self.camLens.setFov(80)

        crosshairs = OnscreenImage(
            image = 'crosshairs.png',
            pos = (0, 0, 0),
            scale = 0.05,
        )
        crosshairs.setTransparency(TransparencyAttrib.MAlpha)

        self.cTrav = CollisionTraverser()
        ray = CollisionRay()
        ray.setFromLens(self.camNode, (0, 0))
        rayNode = CollisionNode('line-of-sight')
        rayNode.addSolid(ray)
        rayNodePath = self.camera.attachNewNode(rayNode)
        self.rayQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(rayNodePath, self.rayQueue)

    def setupSkybox(self):
        skybox = loader.loadModel('skybox/skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)

game = MyGame()
game.run()