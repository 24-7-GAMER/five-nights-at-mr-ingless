-- Five Nights at Mr Ingles's - LOVE2D Edition (Upgraded with Assets & Audio)

-------------------------------------------------------
-- CORE STATE
-------------------------------------------------------
local game = {
    state = "menu",          -- "menu", "playing", "jumpscare", "win"
    night = 1,
    maxNightUnlocked = 1,
    hour = 12,
    hourTimer = 0,
    secondsPerHour = 40,     -- change for shorter/longer nights
    width = 1280,
    height = 720,
    status = "",
}

local power = {
    max = 100,
    current = 100,
    baseDrain = 0.20,
    doorDrain = 0.18,
    lightDrain = 0.20,
    camDrain = 0.15,
    outage = false,
}

local office = {
    doorLeftClosed = false,
    doorRightClosed = false,
    lightOn = true,
    camsOpen = false,
    doorLeftProgress = 0.0,   -- 0 = open, 1 = closed (animated)
    doorRightProgress = 0.0,
    lightDim = 0.0,           -- animated darkness overlay
    camFlash = 0.0,           -- quick static flash when switching cams
}

local cameras = {
    list = { "Cafeteria", "Hallway", "Gym", "Library", "Bathrooms", "Vent" },
    currentIndex = 1,
}

local rooms = {
    "Office", "Hallway", "Cafeteria", "Gym", "Library", "Bathrooms", "Vent"
}

local roomGraph = {
    Office     = { "Hallway" },
    Hallway    = { "Office", "Cafeteria", "Gym", "Bathrooms" },
    Cafeteria  = { "Hallway", "Library" },
    Gym        = { "Hallway" },
    Library    = { "Cafeteria" },
    Bathrooms  = { "Hallway", "Vent" },
    Vent       = { "Bathrooms", "Office" },
}

-- Animatronics table
local anims = {}

-- Fonts
local fontSmall, fontMedium, fontLarge

-- Assets
local img = {}
local sfx = {}
local music = {}
local staticSource = nil
local ambienceSource = nil

-- Jumpscare
local jumpscare = {
    active = false,
    timer = 0,
    duration = 2.0,
    killer = "Mr Ingles",
}

-- Save file
local SAVE_FILE = "mr_ingles_save.txt"

-------------------------------------------------------
-- UTILS
-------------------------------------------------------
local function clamp(x, a, b)
    if x < a then return a end
    if x > b then return b end
    return x
end

local function setStatus(msg)
    game.status = msg or ""
end

local function loadSave()
    if not love.filesystem.getInfo(SAVE_FILE) then
        game.maxNightUnlocked = 1
        return
    end
    local contents = love.filesystem.read(SAVE_FILE)
    if contents then
        local n = tonumber(contents)
        if n and n >= 1 and n <= 5 then
            game.maxNightUnlocked = n
        else
            game.maxNightUnlocked = 1
        end
    end
end

local function saveProgress()
    local toSave = tostring(clamp(game.maxNightUnlocked, 1, 5))
    love.filesystem.write(SAVE_FILE, toSave)
end

-------------------------------------------------------
-- ASSET LOADING (SAFE)
-------------------------------------------------------
local function safeImage(path)
    if love.filesystem.getInfo(path) then
        return love.graphics.newImage(path)
    end
    return nil
end

local function safeSound(path, stype)
    if love.filesystem.getInfo(path) then
        return love.audio.newSource(path, stype or "static")
    end
    return nil
end

local function loadAssets()
    -- Images: office & cams
    img.office        = safeImage("assets/img/office.png")
    img.doorLeft      = safeImage("assets/img/office_door_left.png")
    img.doorRight     = safeImage("assets/img/office_door_right.png")
    img.cam_cafeteria = safeImage("assets/img/cam_cafeteria.png")
    img.cam_hallway   = safeImage("assets/img/cam_hallway.png")
    img.cam_gym       = safeImage("assets/img/cam_gym.png")
    img.cam_library   = safeImage("assets/img/cam_library.png")
    img.cam_bathrooms = safeImage("assets/img/cam_bathrooms.png")
    img.cam_vent      = safeImage("assets/img/cam_vent.png")

    -- Animatronic sprites
    img.anim_mr_ingles = safeImage("assets/img/anim_mr_ingles.png")
    img.anim_janitor   = safeImage("assets/img/anim_janitor.png")
    img.anim_librarian = safeImage("assets/img/anim_librarian.png")
    img.anim_vent      = safeImage("assets/img/anim_vent.png")
    img.mr_ingles_office = safeImage("assets/img/mr_ingles_office.png")

    -- SFX
    sfx.doorClose   = safeSound("assets/sfx/door_close.ogg", "static")
    sfx.doorOpen    = safeSound("assets/sfx/door_open.ogg", "static")
    sfx.lightToggle = safeSound("assets/sfx/light_toggle.ogg", "static")
    sfx.jumpscare   = safeSound("assets/sfx/jumpscare.ogg", "static")
    sfx.bell6am     = safeSound("assets/sfx/bell_6am.ogg", "static")
    sfx.staticLoop  = safeSound("assets/sfx/static_loop.ogg", "stream")

    -- Ambience per night
    music.n1 = safeSound("assets/sfx/ambience_n1.ogg", "stream")
    music.n2 = safeSound("assets/sfx/ambience_n2.ogg", "stream")
    music.n3 = safeSound("assets/sfx/ambience_n3.ogg", "stream")
    music.n4 = safeSound("assets/sfx/ambience_n4.ogg", "stream")
    music.n5 = safeSound("assets/sfx/ambience_n5.ogg", "stream")

    -- Menu music (you must have assets/music/menu_theme.ogg)
    music.menu = safeSound("assets/music/menu_theme.ogg", "stream")
end

local function playSfx(source)
    if source then
        source:stop()
        source:play()
    end
end

local function stopSource(src)
    if src and src:isPlaying() then src:stop() end
end

local function playStaticLoop()
    if sfx.staticLoop then
        staticSource = sfx.staticLoop
        staticSource:setLooping(true)
        staticSource:setVolume(0.4)
        staticSource:play()
    end
end

local function stopStaticLoop()
    if staticSource then
        staticSource:stop()
    end
end

local function playAmbienceForNight(night)
    if ambienceSource then
        stopSource(ambienceSource)
        ambienceSource = nil
    end
    local key = "n"..tostring(clamp(night, 1, 5))
    local src = music[key]
    if src then
        ambienceSource = src
        ambienceSource:setLooping(true)
        ambienceSource:setVolume(0.6)
        ambienceSource:play()
    end
end

-- Menu music helpers
local function playMenuMusic()
    if music.menu then
        if ambienceSource then
            stopSource(ambienceSource)
        end
        ambienceSource = music.menu
        ambienceSource:setLooping(true)
        ambienceSource:setVolume(0.6)
        ambienceSource:play()
    end
end

local function stopMenuMusic()
    if ambienceSource and ambienceSource == music.menu then
        stopSource(ambienceSource)
        ambienceSource = nil
    end
end

-------------------------------------------------------
-- ANIMATRONICS
-------------------------------------------------------
local function roomPos(room)
    local W, H = game.width, game.height
    if room == "Office"   then return W*0.5, H*0.7 end
    if room == "Hallway"  then return W*0.5, H*0.4 end
    if room == "Cafeteria"then return W*0.3, H*0.4 end
    if room == "Gym"      then return W*0.7, H*0.4 end
    if room == "Library"  then return W*0.25, H*0.3 end
    if room == "Bathrooms"then return W*0.75, H*0.3 end
    if room == "Vent"     then return W*0.5, H*0.2 end
    return W*0.5, H*0.5
end

local function neighbors(room)
    return roomGraph[room] or {}
end

local function makeAnim(name, startRoom, baseAggro, baseInterval, style)
    local x, y = roomPos(startRoom)
    return {
        name = name,
        room = startRoom,
        baseAggro = baseAggro,
        baseInterval = baseInterval,
        aggro = baseAggro,
        moveInterval = baseInterval,
        timer = 0,
        style = style or "teleport",
        x = x,
        y = y,
        targetX = x,
        targetY = y,
        visibleOnCam = true,
    }
end

local function resetAnimatronics()
    anims = {
        makeAnim("Mr Ingles",    "Cafeteria",  0.35, 6.0,  "teleport"),
        makeAnim("Janitor Bot",  "Bathrooms",  0.30, 7.0,  "teleport"),
        makeAnim("Librarian",    "Library",    0.25, 8.0,  "teleport"),
        makeAnim("Vent Crawler", "Vent",       0.40, 5.0,  "vent"),
    }
end

local function setupAnimatronics()
    resetAnimatronics()
end

local function updateOfficeEffects(dt)
    -- Smoothly animate door movement to avoid popping
    local doorSpeed = 5 * dt
    local leftTarget = office.doorLeftClosed and 1 or 0
    local rightTarget = office.doorRightClosed and 1 or 0
    office.doorLeftProgress = office.doorLeftProgress + (leftTarget - office.doorLeftProgress) * doorSpeed
    office.doorRightProgress = office.doorRightProgress + (rightTarget - office.doorRightProgress) * doorSpeed

    -- Smooth light dimming for flashlight toggle
    local dimTarget = office.lightOn and 0 or 0.6
    local dimSpeed = 3 * dt
    office.lightDim = office.lightDim + (dimTarget - office.lightDim) * dimSpeed

    -- Fade out the camera static flash
    if office.camFlash > 0 then
        office.camFlash = math.max(0, office.camFlash - dt * 2.8)
    end
end

local function moveAnim(a)
    local neigh = neighbors(a.room)
    if #neigh == 0 then return end
    local idx = love.math.random(1, #neigh)
    a.room = neigh[idx]
    a.targetX, a.targetY = roomPos(a.room)
end

local function tryAttack(a)
    if a.room == "Office" then
        if a.name == "Vent Crawler" then
            -- Vent ignores doors
            jumpscare.killer = a.name
            jumpscare.active = true
            jumpscare.timer = 0
            game.state = "jumpscare"
            playSfx(sfx.jumpscare)
            stopStaticLoop()
            stopSource(ambienceSource)
            return
        end

        if not office.doorLeftClosed or not office.doorRightClosed then
            jumpscare.killer = a.name
            jumpscare.active = true
            jumpscare.timer = 0
            game.state = "jumpscare"
            playSfx(sfx.jumpscare)
            stopStaticLoop()
            stopSource(ambienceSource)
        end
    end
end

local function updateAnim(a, dt)
    a.timer = a.timer + dt
    local interval = a.moveInterval
    local chance = a.aggro

    if a.timer >= interval then
        a.timer = a.timer - interval
        if love.math.random() < chance then
            moveAnim(a)
            tryAttack(a)
        end
    end

    -- Smooth position toward target
    local speed = 4 * dt
    a.x = a.x + (a.targetX - a.x) * speed
    a.y = a.y + (a.targetY - a.y) * speed
end

local function updateAnims(dt)
    for _, a in ipairs(anims) do
        updateAnim(a, dt)
    end
end

-------------------------------------------------------
-- POWER & TIME
-------------------------------------------------------
local function resetPower()
    power.current = power.max
    power.outage = false
end

local function updatePower(dt)
    if game.state ~= "playing" then return end
    if power.current <= 0 then
        power.current = 0
        if not power.outage then
            power.outage = true
            office.doorLeftClosed = false
            office.doorRightClosed = false
            office.lightOn = false
            office.camsOpen = false
            setStatus("POWER OUTAGE.")
            stopStaticLoop()
        end
        return
    end

    local drain = power.baseDrain
    if office.doorLeftClosed or office.doorRightClosed then
        drain = drain + power.doorDrain
    end
    if office.lightOn then
        drain = drain + power.lightDrain
    end
    if office.camsOpen then
        drain = drain + power.camDrain
    end

    power.current = power.current - drain * dt
    if power.current < 0 then power.current = 0 end
end

local function resetTime()
    game.hour = 12
    game.hourTimer = 0
end

local function updateTime(dt)
    if game.state ~= "playing" then return end
    game.hourTimer = game.hourTimer + dt
    if game.hourTimer >= game.secondsPerHour then
        game.hourTimer = game.hourTimer - game.secondsPerHour
        game.hour = game.hour + 1
        if game.hour >= 6 then
            game.state = "win"
            setStatus("6 AM! You survived Night " .. tostring(game.night) .. "!")
            playSfx(sfx.bell6am)
            stopStaticLoop()
            stopSource(ambienceSource)
            if game.night < 5 and game.night + 1 > game.maxNightUnlocked then
                game.maxNightUnlocked = game.night + 1
                saveProgress()
            end
        end
    end
end

-------------------------------------------------------
-- GAME FLOW
-------------------------------------------------------
local function startNight(n)
    stopMenuMusic()
    game.night = clamp(n, 1, 5)
    game.state = "playing"
    setStatus("")
    resetPower()
    resetTime()
    setupAnimatronics()
    jumpscare.active = false
    office.doorLeftClosed = false
    office.doorRightClosed = false
    office.lightOn = true
    office.camsOpen = false
    office.doorLeftProgress = 0
    office.doorRightProgress = 0
    office.lightDim = 0
    office.camFlash = 0
    stopStaticLoop()
    playAmbienceForNight(game.night)
end

local function restartFromMenu()
    game.state = "menu"
    setStatus("")
    stopStaticLoop()
    stopSource(ambienceSource)
    playMenuMusic()
end

-------------------------------------------------------
-- LOVE CALLBACKS
-------------------------------------------------------
function love.load()
    love.window.setMode(game.width, game.height)
    love.window.setTitle("Five Nights at Mr Ingles's  (LOVE2D Edition)")

    fontSmall  = love.graphics.newFont(14)
    fontMedium = love.graphics.newFont(24)
    fontLarge  = love.graphics.newFont(40)

    loadAssets()
    loadSave()

    if game.state == "menu" then
        playMenuMusic()
    end
end

function love.update(dt)
    if game.state == "menu" then
        return
    end

    if game.state == "playing" then
        updatePower(dt)
        updateTime(dt)
        updateAnims(dt)
    elseif game.state == "jumpscare" then
        jumpscare.timer = jumpscare.timer + dt
    elseif game.state == "win" then
        -- nothing special
    end

    if game.state == "playing" then
        updateOfficeEffects(dt)
    end
end

-------------------------------------------------------
-- DRAWING
-------------------------------------------------------
local function drawBackground()
    love.graphics.setColor(1, 1, 1)
    if img.office then
        love.graphics.draw(img.office, 0, 0, 0,
            game.width / img.office:getWidth(),
            game.height / img.office:getHeight())
    else
        love.graphics.clear(0.05, 0.05, 0.05)
    end
end

local animSprites = {
    ["Mr Ingles"]   = function() return img.anim_mr_ingles or img.mr_ingles_office end,
    ["Janitor Bot"] = function() return img.anim_janitor end,
    ["Librarian"]   = function() return img.anim_librarian end,
    ["Vent Crawler"] = function() return img.anim_vent end,
}

local function getAnimSprite(name)
    local getter = animSprites[name]
    if getter then
        return getter()
    end
    return img.mr_ingles_office
end

local function drawCameraFeed()
    local camName = cameras.list[cameras.currentIndex]
    local camKey = "cam_" .. string.lower(camName)
    local camImg = img[camKey]

    if camImg then
        love.graphics.setColor(1, 1, 1)
        local sx = game.width / camImg:getWidth()
        local sy = game.height / camImg:getHeight()
        love.graphics.draw(camImg, 0, 0, 0, sx, sy)
    else
        love.graphics.setColor(0, 0, 0.1)
        love.graphics.rectangle("fill", 0, 0, game.width, game.height)
    end

    love.graphics.setFont(fontMedium)
    love.graphics.setColor(0, 1, 1)
    love.graphics.print("CAM: " .. camName, 20, 20)

    local now = love.timer.getTime()
    for _, a in ipairs(anims) do
        if a.room == camName then
            local sprite = getAnimSprite(a.name)
            if sprite then
                love.graphics.setColor(1, 1, 1)
                local iw, ih = sprite:getWidth(), sprite:getHeight()
                local wobble = math.sin(now * 2 + a.x * 0.01) * 0.02
                local baseScale = 0.42
                local sx = baseScale * (game.width / 1280)
                local sy = baseScale * (game.height / 720)

                -- draw sprite
                love.graphics.draw(sprite, a.x, a.y + wobble * 30, wobble,
                    sx * (1 + wobble), sy * (1 + wobble), iw / 2, ih / 2)
            else
                love.graphics.setColor(0.7, 1, 1)
                love.graphics.circle("fill", a.x, a.y, 20)
            end
        end
    end

    love.graphics.setColor(0, 1, 1, 0.08)
    for y = 0, game.height, 8 do
        love.graphics.line(0, y, game.width, y)
    end

    if office.camFlash > 0 then
        love.graphics.setColor(1, 1, 1, 0.8 * office.camFlash)
        love.graphics.rectangle("fill", 0, 0, game.width, game.height)
        love.graphics.setColor(0, 0, 0.2, 0.4 * office.camFlash)

        for i = 1, 30 do
            local x = love.math.random() * game.width
            local y = love.math.random() * game.height
            local w = love.math.random(4, 14)
            love.graphics.rectangle("fill", x, y, w, 2)
        end
    end
end

local function drawOfficeView()
    for _, a in ipairs(anims) do
        if a.room == "Hallway" or a.room == "Office" then
            local sprite = getAnimSprite(a.name)

            if sprite then
                love.graphics.setColor(1, 1, 1)
                local iw, ih = sprite:getWidth(), sprite:getHeight()
                local scale = 0.4
                local wobble = math.sin(love.timer.getTime() * 2 + a.x * 0.01) * 0.02
                local sx = scale * (game.width / 1280)
                local sy = scale * (game.height / 720)
                love.graphics.draw(
                    sprite,
                    a.x,
                    a.y + wobble * 40,
                    wobble,
                    sx * (1 + wobble),
                    sy * (1 + wobble),
                    iw / 2,
                    ih / 2
                )
            else
                love.graphics.setColor(1, 0, 0)
                love.graphics.circle("fill", a.x, a.y, 25)
            end
        end
    end

    -- Doors overlay the office (left and right)
    if (office.doorLeftClosed or office.doorLeftProgress > 0.01) and img.doorLeft then
        local scale = game.height / img.doorLeft:getHeight()
        love.graphics.setColor(1, 1, 1)
        local slide = 1 - office.doorLeftProgress
        love.graphics.draw(img.doorLeft, -img.doorLeft:getWidth() * scale * slide, 0, 0, scale, scale)
    end

    if (office.doorRightClosed or office.doorRightProgress > 0.01) and img.doorRight then
        local scale = game.height / img.doorRight:getHeight()
        local dw = img.doorRight:getWidth() * scale
        love.graphics.setColor(1, 1, 1)
        local slide = 1 - office.doorRightProgress
        love.graphics.draw(img.doorRight, game.width - dw + dw * slide, 0, 0, scale, scale)
    end

    -- Light toggle overlays a dim filter when off
    love.graphics.setColor(0, 0, 0, office.lightDim)
    love.graphics.rectangle("fill", 0, 0, game.width, game.height)

    -- Add a soft vignette to make the office feel moodier
    for i = 1, 6 do
        local alpha = 0.05 * i
        love.graphics.setColor(0, 0, 0, alpha)
        love.graphics.rectangle("line", 10 * i, 10 * i, game.width - 20 * i, game.height - 20 * i)
    end
end

local function drawAnims()
    if office.camsOpen then
        drawCameraFeed()
    else
        drawOfficeView()
    end
end

local function drawHUD()
    love.graphics.setFont(fontSmall)
    local p = math.floor(power.current + 0.5)
    if p <= 20 then
        love.graphics.setColor(1, 0, 0)
    else
        love.graphics.setColor(0, 1, 0)
    end
    love.graphics.print("POWER: "..tostring(p).."%", 20, game.height - 40)

    local displayHour = game.hour
    if displayHour == 0 then displayHour = 12 end
    love.graphics.setColor(0.8, 0.8, 1)
    love.graphics.print(tostring(displayHour).." AM", game.width - 90, 20)

    love.graphics.print("Night "..tostring(game.night), 20, 20)

    if game.status ~= "" then
        love.graphics.setColor(1, 1, 0.5)
        love.graphics.setFont(fontMedium)
        love.graphics.printf(game.status, 0, game.height*0.08,
                             game.width, "center")
    end

    love.graphics.setFont(fontSmall)
    love.graphics.setColor(0.7, 0.7, 0.7)
    love.graphics.print("[Q] Left Door  [E] Right Door  [F] Light  [TAB] Cameras  [1-6] Switch Cams",
                        20, game.height - 20)
end

local function drawMenu()
    love.graphics.setColor(0, 0, 0.1)
    love.graphics.rectangle("fill", 0, 0, game.width, game.height)

    love.graphics.setFont(fontLarge)
    love.graphics.setColor(0, 1, 1)
    love.graphics.printf("FIVE NIGHTS AT MR INGLES'S", 0, game.height*0.2,
                         game.width, "center")

    love.graphics.setFont(fontMedium)
    love.graphics.setColor(1, 1, 1)
    love.graphics.printf("Press 1-5 to start a night\n(locked nights are disabled)",
                         0, game.height*0.4, game.width, "center")

    love.graphics.setFont(fontSmall)
    love.graphics.setColor(0.7, 0.7, 0.7)
    local text = "Unlocked nights: 1"
    if game.maxNightUnlocked > 1 then
        text = "Unlocked nights: 1-"..tostring(game.maxNightUnlocked)
    end
    love.graphics.printf(text, 0, game.height*0.55, game.width, "center")
end

local function drawJumpscare()
    love.graphics.setColor(0.3, 0, 0)
    love.graphics.rectangle("fill", 0, 0, game.width, game.height)

    local alpha = 0.5 + 0.5 * math.sin(jumpscare.timer * 30)
    love.graphics.setColor(1, 0, 0, alpha)
    love.graphics.rectangle("fill", 0, 0, game.width, game.height)

    love.graphics.setFont(fontLarge)
    love.graphics.setColor(1, 1, 1)
    love.graphics.printf(jumpscare.killer.." GOT YOU!", 0, game.height*0.3,
                         game.width, "center")

    love.graphics.setFont(fontMedium)
    love.graphics.printf("Press [R] to restart Night 1  |  [M] for Menu",
                         0, game.height*0.6, game.width, "center")
end

local function drawWin()
    love.graphics.setColor(0, 0.1, 0)
    love.graphics.rectangle("fill", 0, 0, game.width, game.height)

    love.graphics.setFont(fontLarge)
    love.graphics.setColor(0.6, 1, 0.6)
    love.graphics.printf("6 AM", 0, game.height*0.3, game.width, "center")

    love.graphics.setFont(fontMedium)
    love.graphics.printf("You survived Night "..tostring(game.night).."!",
                         0, game.height*0.4, game.width, "center")

    love.graphics.setFont(fontSmall)
    love.graphics.setColor(1, 1, 1)
    love.graphics.printf("Press [R] to restart Night 1  |  [M] for Menu",
                         0, game.height*0.6, game.width, "center")
end

-------------------------------------------------------
-- LOVE DRAW
-------------------------------------------------------
function love.draw()
    if game.state == "menu" then
        drawMenu()
        return
    end

    if game.state == "jumpscare" then
        drawJumpscare()
        return
    end

    if game.state == "win" then
        drawWin()
        return
    end

    drawBackground()
    drawAnims()
    drawHUD()
end

-------------------------------------------------------
-- INPUT
-------------------------------------------------------
local function toggleDoor(side)
    if power.outage then return end
    if side == "left" then
        office.doorLeftClosed = not office.doorLeftClosed
        playSfx(office.doorLeftClosed and sfx.doorClose or sfx.doorOpen)
    elseif side == "right" then
        office.doorRightClosed = not office.doorRightClosed
        playSfx(office.doorRightClosed and sfx.doorClose or sfx.doorOpen)
    end
end

local function toggleFlashlight()
    if power.outage then return end
    office.lightOn = not office.lightOn
    playSfx(sfx.lightToggle)
end

local function toggleCameras()
    if power.outage then return end
    office.camsOpen = not office.camsOpen
    if office.camsOpen then
        office.camFlash = 1
        playStaticLoop()
    else
        stopStaticLoop()
    end
end

local function switchCamera(index)
    if index < 1 or index > #cameras.list then return end
    cameras.currentIndex = index
    if office.camsOpen then
        office.camFlash = 1
    end
end

function love.keypressed(key)
    if key == "escape" then
        love.event.quit()
        return
    end

    if game.state == "menu" then
        if key == "1" then
            startNight(1)
        elseif key == "2" and game.maxNightUnlocked >= 2 then
            startNight(2)
        elseif key == "3" and game.maxNightUnlocked >= 3 then
            startNight(3)
        elseif key == "4" and game.maxNightUnlocked >= 4 then
            startNight(4)
        elseif key == "5" and game.maxNightUnlocked >= 5 then
            startNight(5)
        end
        return
    end

    if game.state == "playing" then
        if key == "q" then
            toggleDoor("left")
        elseif key == "e" then
            toggleDoor("right")
        elseif key == "f" then
            toggleFlashlight()
        elseif key == "tab" then
            toggleCameras()
        elseif key == "1" then
            switchCamera(1)
        elseif key == "2" then
            switchCamera(2)
        elseif key == "3" then
            switchCamera(3)
        elseif key == "4" then
            switchCamera(4)
        elseif key == "5" then
            switchCamera(5)
        elseif key == "6" then
            switchCamera(6)
        end
    elseif game.state == "jumpscare" then
        if key == "r" then
            startNight(1)
        elseif key == "m" then
            restartFromMenu()
        end
    elseif game.state == "win" then
        if key == "r" then
            startNight(1)
        elseif key == "m" then
            restartFromMenu()
        end
    end
end
