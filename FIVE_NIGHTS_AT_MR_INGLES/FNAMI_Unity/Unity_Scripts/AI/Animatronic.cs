using UnityEngine;
using System.Collections.Generic;
using System.Collections;
using System;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Animatronic AI controller with advanced behavior
    /// Converted from Python Animatronic class
    /// </summary>
    public class Animatronic : MonoBehaviour
    {
        #region Enums
        public enum AnimatronicMood
        {
            Neutral,
            Aggressive,
            Cautious,
            Hunting,
            Retreating
        }

        public enum AIPersonality
        {
            Aggressive,    // Moves fast, attacks often
            Patient,       // Waits for perfect opportunity
            Erratic,       // Unpredictable movements
            Stalker,       // Follows player patterns
            TeamPlayer,    // Coordinates with others
            Trickster,     // Uses fake movements
            Cautious,      // Retreats often, slow approach
            Relentless     // Never gives up, constant pressure
        }

        public enum SpecialAbility
        {
            LightKiller,     // Can disable lights temporarily
            CameraJammer,    // Can jam cameras
            PowerDrainer,    // Extra power drain
            SpeedDemon,      // Periodic speed boosts
            DoorBreaker,     // Extra damage to doors
            SilentStalker,   // Makes no sound when moving
            Mimic,           // Can appear in multiple cameras
            Teleporter       // Can skip rooms
        }

        public enum MovementStyle
        {
            Teleport,   // Instant room changes
            Patrol,     // Follows patrol route
            Wander,     // Random movement
            Hunter      // Moves toward player
        }
        #endregion

        #region Public Fields
        [Header("Identity")]
        public string characterName = "Mr Ingles";
        public Sprite characterSprite;
        public float sizeMultiplier = 1.0f;

        [Header("Starting Configuration")]
        public RoomData startingRoom;
        public List<RoomData> patrolRoute = new List<RoomData>();
        public float startDelayMinutes = 0f; // Delay before activating

        [Header("AI Settings")]
        public float baseAggression = 1.0f;
        public float baseMoveInterval = 5.0f;
        public MovementStyle movementStyle = MovementStyle.Patrol;
        public AIPersonality personality = AIPersonality.Aggressive;
        public SpecialAbility specialAbility = SpecialAbility.SpeedDemon;

        [Header("Attack Settings")]
        public bool attackFromLeft = true; // Which door to attack from
        public float hallwayEntryDelay = 2.0f;
        public float attackWindupRequired = 1.2f;
        
        [Header("Current State")]
        public RoomData currentRoom;
        public int currentPatrolIndex = 0;
        public AnimatronicMood currentMood = AnimatronicMood.Neutral;
        public bool isActive = false;
        #endregion

        #region Private Fields
        private float moveTimer = 0f;
        private float moveCooldown = 5f;
        private float moodTimer = 0f;
        private float hallwayTimer = 0f;
        private float attackWindup = 0f;
        private float huntingTimer = 0f;
        private float retreatTimer = 0f;
        private float adaptiveAggression = 1.0f;
        private int blockCount = 0;
        private bool isInHallway = false;
        private bool isHunting = false;
        private RoomData huntTarget = null;

        // Personality traits (randomized)
        private float patience;
        private float curiosity;
        private float persistence;
        private float teamwork;
        private float deception;
        private float soundSensitivity;
        private float cameraAwareness;

        private System.Random rng;
        #endregion

        #region Events
        public static event Action<Animatronic, RoomData> OnAnimatronicMove;
        public static event Action<Animatronic> OnAnimatronicAttack;
        public static event Action<Animatronic, RoomData> OnAnimatronicSpotted;
        #endregion

        #region Initialization
        void Start()
        {
            // Initialize with seed based on name for deterministic behavior
            int seed = characterName.GetHashCode() + GameManager.Instance.currentNight;
            rng = new System.Random(seed);
            
            currentRoom = startingRoom;
            
            // Randomize personality traits
            InitializePersonalityTraits();
            
            // Calculate initial move cooldown
            UpdateMoveCooldown();
            
            Debug.Log($"{characterName} initialized. Personality: {personality}, Ability: {specialAbility}");
        }

        void InitializePersonalityTraits()
        {
            patience = (float)(rng.NextDouble() * 1.5 + 0.5);       // 0.5 - 2.0
            curiosity = (float)(rng.NextDouble() * 1.2 + 0.3);      // 0.3 - 1.5
            persistence = (float)(rng.NextDouble() * 1.4 + 0.4);    // 0.4 - 1.8
            teamwork = (float)(rng.NextDouble() * 1.1 + 0.2);       // 0.2 - 1.3
            deception = (float)(rng.NextDouble() * 1.1 + 0.1);      // 0.1 - 1.2
            soundSensitivity = (float)(rng.NextDouble() * 1.0 + 0.5); // 0.5 - 1.5
            cameraAwareness = (float)(rng.NextDouble() * 1.1 + 0.3);  // 0.3 - 1.4
        }
        #endregion

        #region Unity Lifecycle
        void Update()
        {
            if (GameManager.Instance == null || GameManager.Instance.currentState != GameManager.GameState.Playing)
                return;
            
            // Check activation delay
            if (!isActive)
            {
                if (GameManager.Instance.minutesElapsed >= startDelayMinutes)
                {
                    isActive = true;
                    Debug.Log($"{characterName} is now ACTIVE!");
                }
                else
                {
                    return; // Wait until start delay passes
                }
            }
            
            UpdateAI();
        }

        void UpdateAI()
        {
            float dt = Time.deltaTime;
            
            moveTimer += dt;
            moodTimer += dt;
            
            // Update mood periodically
            if (moodTimer >= 2f)
            {
                UpdateMood();
                moodTimer = 0f;
            }
            
            // Update adaptive aggression based on player actions
            UpdateAdaptiveAggression();
            
            // Handle retreat state
            if (retreatTimer > 0f)
            {
                retreatTimer -= dt;
                return; // Don't move while retreating
            }
            
            // Handle hunting mode
            if (huntingTimer > 0f)
            {
                huntingTimer -= dt;
                isHunting = huntingTimer > 0f;
            }
            
            // Check if should move
            if (moveTimer >= moveCooldown)
            {
                moveTimer = 0f;
                AttemptMove();
                UpdateMoveCooldown();
            }
            
            // Check if in hallway and ready to attack
            CheckHallwayAttack(dt);
        }
        #endregion

        #region Movement
        void AttemptMove()
        {
            if (currentRoom == null)
            {
                Debug.LogWarning($"{characterName} has no current room!");
                return;
            }
            
            RoomData nextRoom = null;
            
            // Choose movement based on style and mood
            if (isHunting || currentMood == AnimatronicMood.Hunting)
            {
                nextRoom = MoveTowardTarget(huntTarget);
            }
            else if (currentMood == AnimatronicMood.Retreating)
            {
                nextRoom = MoveAwayFromOffice();
            }
            else
            {
                switch (movementStyle)
                {
                    case MovementStyle.Patrol:
                        nextRoom = MovePatrol();
                        break;
                    case MovementStyle.Wander:
                        nextRoom = MoveWander();
                        break;
                    case MovementStyle.Hunter:
                        nextRoom = MoveTowardTarget(null);
                        break;
                    case MovementStyle.Teleport:
                        nextRoom = MoveTeleport();
                        break;
                }
            }
            
            // Execute move if valid
            if (nextRoom != null && nextRoom != currentRoom)
            {
                MoveTo(nextRoom);
            }
        }

        RoomData MovePatrol()
        {
            if (patrolRoute.Count == 0)
                return MoveWander();
            
            currentPatrolIndex = (currentPatrolIndex + 1) % patrolRoute.Count;
            return patrolRoute[currentPatrolIndex];
        }

        RoomData MoveWander()
        {
            if (currentRoom.connectedRooms.Count == 0)
                return null;
            
            int randomIndex = rng.Next(0, currentRoom.connectedRooms.Count);
            return currentRoom.connectedRooms[randomIndex];
        }

        RoomData MoveTowardTarget(RoomData target)
        {
            // Default target is office
            if (target == null)
            {
                target = CameraSystem.Instance?.GetRoomByName("Office");
            }
            
            if (target == null || currentRoom == target)
                return null;
            
            // Simple pathfinding: move to connected room closest to target
            RoomData closestRoom = null;
            float closestDistance = float.MaxValue;
            
            foreach (var connectedRoom in currentRoom.connectedRooms)
            {
                float distance = Vector2.Distance(
                    new Vector2(connectedRoom.minimapX, connectedRoom.minimapY),
                    new Vector2(target.minimapX, target.minimapY)
                );
                
                if (distance < closestDistance)
                {
                    closestDistance = distance;
                    closestRoom = connectedRoom;
                }
            }
            
            return closestRoom;
        }

        RoomData MoveAwayFromOffice()
        {
            RoomData office = CameraSystem.Instance?.GetRoomByName("Office");
            if (office == null)
                return MoveWander();
            
            // Move to room farthest from office
            RoomData farthestRoom = null;
            float maxDistance = 0f;
            
            foreach (var connectedRoom in currentRoom.connectedRooms)
            {
                float distance = Vector2.Distance(
                    new Vector2(connectedRoom.minimapX, connectedRoom.minimapY),
                    new Vector2(office.minimapX, office.minimapY)
                );
                
                if (distance > maxDistance)
                {
                    maxDistance = distance;
                    farthestRoom = connectedRoom;
                }
            }
            
            return farthestRoom;
        }

        RoomData MoveTeleport()
        {
            // Teleport to any random room (special ability style)
            if (CameraSystem.Instance == null || CameraSystem.Instance.allRooms.Count == 0)
                return null;
            
            int randomIndex = rng.Next(0, CameraSystem.Instance.allRooms.Count);
            return CameraSystem.Instance.allRooms[randomIndex];
        }

        void MoveTo(RoomData newRoom)
        {
            RoomData previousRoom = currentRoom;
            currentRoom = newRoom;
            
            Debug.Log($"{characterName} moved: {previousRoom?.roomName} → {newRoom.roomName}");
            
            OnAnimatronicMove?.Invoke(this, newRoom);
            
            // Check if entered a hallway adjacent to office
            if (newRoom.roomName.Contains("Hall") && newRoom.roomName.Contains(attackFromLeft ? "West" : "East"))
            {
                isInHallway = true;
                hallwayTimer = 0f;
                Debug.Log($"{characterName} is in the {(attackFromLeft ? "left" : "right")} hallway!");
            }
            else
            {
                isInHallway = false;
            }
        }
        #endregion

        #region Attack
        void CheckHallwayAttack(float dt)
        {
            if (!isInHallway)
                return;
            
            hallwayTimer += dt;
            
            // Check if door is closed
            bool doorClosed = attackFromLeft ? 
                OfficeController.Instance.doorLeftClosed : 
                OfficeController.Instance.doorRightClosed;
            
            if (doorClosed)
            {
                // Door is closed - we're blocked!
                HandleBlocked();
                return;
            }
            
            // Door is open - start attack windup
            if (hallwayTimer >= hallwayEntryDelay)
            {
                attackWindup += dt;
                
                if (attackWindup >= attackWindupRequired)
                {
                    ExecuteAttack();
                }
            }
        }

        void ExecuteAttack()
        {
            Debug.LogWarning($"{characterName} is ATTACKING!");
            
            OnAnimatronicAttack?.Invoke(this);
            GameManager.Instance?.TriggerJumpscare(characterName);
        }

        void HandleBlocked()
        {
            blockCount++;
            Debug.Log($"{characterName} was blocked by door! (Block count: {blockCount})");
            
            // Retreat based on personality
            if (personality == AIPersonality.Cautious || rng.NextDouble() < 0.3)
            {
                currentMood = AnimatronicMood.Retreating;
                retreatTimer = 3f + (float)rng.NextDouble() * 2f;
                isInHallway = false;
                hallwayTimer = 0f;
                attackWindup = 0f;
            }
            else if (personality == AIPersonality.Relentless || persistence > 1.5f)
            {
                // Stay in hallway, try again
                hallwayTimer = 0f;
                attackWindup = 0f;
            }
        }
        #endregion

        #region AI Behavior
        void UpdateMood()
        {
            // Mood changes based on situation and personality
            float random = (float)rng.NextDouble();
            
            if (isHunting)
            {
                currentMood = AnimatronicMood.Hunting;
            }
            else if (random < 0.1f && personality == AIPersonality.Aggressive)
            {
                currentMood = AnimatronicMood.Aggressive;
            }
            else if (random < 0.15f && personality == AIPersonality.Cautious)
            {
                currentMood = AnimatronicMood.Cautious;
            }
            else
            {
                currentMood = AnimatronicMood.Neutral;
            }
        }

        void UpdateAdaptiveAggression()
        {
            // Increase aggression as night progresses and based on blocks
            float nightProgress = GameManager.Instance?.GetNightProgress() ?? 0f;
            float timeFactor = nightProgress * 0.5f;
            float blockFactor = blockCount * 0.05f;
            
            adaptiveAggression = baseAggression * GameManager.Instance.difficulty + timeFactor + blockFactor;
            adaptiveAggression = Mathf.Min(adaptiveAggression, 2.5f);
        }

        void UpdateMoveCooldown()
        {
            float difficulty = GameManager.Instance?.difficulty ?? 1f;
            float cooldown = baseMoveInterval / Mathf.Max(0.5f, difficulty) / (1f + adaptiveAggression * 0.4f);
            cooldown *= patience; // Personality modifier
            
            moveCooldown = Mathf.Max(0.5f, cooldown);
        }
        #endregion

        #region Public Methods
        public void StartHunting(RoomData targetRoom, float duration)
        {
            huntTarget = targetRoom;
            huntingTimer = duration;
            isHunting = true;
            currentMood = AnimatronicMood.Hunting;
            
            Debug.Log($"{characterName} is now HUNTING {targetRoom?.roomName}!");
        }

        public void ForceRetreat(float duration)
        {
            currentMood = AnimatronicMood.Retreating;
            retreatTimer = duration;
            isInHallway = false;
            
            Debug.Log($"{characterName} is RETREATING for {duration:F1} seconds!");
        }

        public void ResetAnimatronic()
        {
            currentRoom = startingRoom;
            currentPatrolIndex = 0;
            isActive = false;
            isInHallway = false;
            isHunting = false;
            moveTimer = 0f;
            hallwayTimer = 0f;
            attackWindup = 0f;
            huntingTimer = 0f;
            retreatTimer = 0f;
            blockCount = 0;
            currentMood = AnimatronicMood.Neutral;
            
            Debug.Log($"{characterName} reset to starting position.");
        }
        #endregion

        #region Debug
        [ContextMenu("Force Move to Office")]
        void DebugMoveToOffice()
        {
            RoomData office = CameraSystem.Instance?.GetRoomByName("Office");
            if (office != null)
            {
                MoveTo(office);
            }
        }

        [ContextMenu("Trigger Attack")]
        void DebugTriggerAttack()
        {
            ExecuteAttack();
        }

        [ContextMenu("Start Hunting Office")]
        void DebugHuntOffice()
        {
            RoomData office = CameraSystem.Instance?.GetRoomByName("Office");
            StartHunting(office, 30f);
        }
        #endregion
    }
}
