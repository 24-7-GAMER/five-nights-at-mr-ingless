using UnityEngine;
using System.Collections.Generic;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Manages all animatronics in the scene
    /// </summary>
    public class AnimatronicManager : MonoBehaviour
    {
        #region Singleton
        public static AnimatronicManager Instance { get; private set; }

        void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }
        #endregion

        #region Public Fields
        [Header("Animatronics")]
        public List<Animatronic> animatronics = new List<Animatronic>();

        [Header("Difficulty Scaling")]
        public bool scaleDifficultyWithNight = true;
        public float difficultyPerNight = 0.2f;

        [Header("Coordination")]
        public bool enableTeamwork = true;
        public float coordinationRange = 0.3f; // Map distance for coordination
        #endregion

        #region Private Fields
        private Dictionary<RoomData, List<Animatronic>> roomOccupancy = new Dictionary<RoomData, List<Animatronic>>();
        #endregion

        #region Unity Lifecycle
        void OnEnable()
        {
            GameManager.OnNightStart += HandleNightStart;
            Animatronic.OnAnimatronicMove += HandleAnimatronicMove;
        }

        void OnDisable()
        {
            GameManager.OnNightStart -= HandleNightStart;
            Animatronic.OnAnimatronicMove -= HandleAnimatronicMove;
        }

        void Start()
        {
            DiscoverAnimatronics();
            UpdateRoomOccupancy();
        }

        void Update()
        {
            if (GameManager.Instance == null || GameManager.Instance.currentState != GameManager.GameState.Playing)
                return;

            if (enableTeamwork)
            {
                UpdateTeamCoordination();
            }
        }
        #endregion

        #region Initialization
        void DiscoverAnimatronics()
        {
            // Find all animatronics in scene
            Animatronic[] foundAnimatronics = FindObjectsOfType<Animatronic>();

            animatronics.Clear();
            animatronics.AddRange(foundAnimatronics);

            Debug.Log($"AnimatronicManager discovered {animatronics.Count} animatronics");
        }
        #endregion

        #region Event Handlers
        void HandleNightStart(int night)
        {
            // Reset all animatronics
            foreach (var animatronic in animatronics)
            {
                if (animatronic != null)
                {
                    animatronic.ResetAnimatronic();
                }
            }

            // Apply difficulty scaling
            if (scaleDifficultyWithNight && GameManager.Instance != null)
            {
                float nightModifier = (night - 1) * difficultyPerNight;
                float totalDifficulty = GameManager.Instance.difficulty + nightModifier;

                Debug.Log($"Night {night} difficulty: {totalDifficulty:F2}");
            }

            UpdateRoomOccupancy();
        }

        void HandleAnimatronicMove(Animatronic animatronic, RoomData newRoom)
        {
            UpdateRoomOccupancy();

            // Log movement for debugging
            Debug.Log($"[AnimatronicManager] {animatronic.characterName} → {newRoom.roomName}");
        }
        #endregion

        #region Room Occupancy
        void UpdateRoomOccupancy()
        {
            roomOccupancy.Clear();

            foreach (var animatronic in animatronics)
            {
                if (animatronic == null || animatronic.currentRoom == null)
                    continue;

                if (!roomOccupancy.ContainsKey(animatronic.currentRoom))
                {
                    roomOccupancy[animatronic.currentRoom] = new List<Animatronic>();
                }

                roomOccupancy[animatronic.currentRoom].Add(animatronic);
            }
        }

        public List<Animatronic> GetAnimatronicsInRoom(RoomData room)
        {
            if (room == null)
                return new List<Animatronic>();

            if (roomOccupancy.ContainsKey(room))
            {
                return new List<Animatronic>(roomOccupancy[room]);
            }

            return new List<Animatronic>();
        }

        public int GetAnimatronicCountInRoom(RoomData room)
        {
            if (room == null || !roomOccupancy.ContainsKey(room))
                return 0;

            return roomOccupancy[room].Count;
        }
        #endregion

        #region Teamwork/Coordination
        void UpdateTeamCoordination()
        {
            // Animatronics can coordinate attacks if they're near each other
            foreach (var animatronic in animatronics)
            {
                if (animatronic == null || !animatronic.isActive)
                    continue;

                // Find nearby animatronics
                List<Animatronic> nearbyAnimatronics = GetNearbyAnimatronics(animatronic, coordinationRange);

                if (nearbyAnimatronics.Count > 0)
                {
                    // Coordination logic
                    HandleTeamCoordination(animatronic, nearbyAnimatronics);
                }
            }
        }

        List<Animatronic> GetNearbyAnimatronics(Animatronic target, float range)
        {
            List<Animatronic> nearby = new List<Animatronic>();

            if (target.currentRoom == null)
                return nearby;

            Vector2 targetPos = new Vector2(target.currentRoom.minimapX, target.currentRoom.minimapY);

            foreach (var other in animatronics)
            {
                if (other == null || other == target || !other.isActive || other.currentRoom == null)
                    continue;

                Vector2 otherPos = new Vector2(other.currentRoom.minimapX, other.currentRoom.minimapY);
                float distance = Vector2.Distance(targetPos, otherPos);

                if (distance <= range)
                {
                    nearby.Add(other);
                }
            }

            return nearby;
        }

        void HandleTeamCoordination(Animatronic leader, List<Animatronic> team)
        {
            // Example: If multiple animatronics are near office, coordinate attack
            RoomData office = CameraSystem.Instance?.GetRoomByName("Office");
            if (office == null)
                return;

            bool nearOffice = false;
            Vector2 officePos = new Vector2(office.minimapX, office.minimapY);
            Vector2 leaderPos = new Vector2(leader.currentRoom.minimapX, leader.currentRoom.minimapY);

            if (Vector2.Distance(leaderPos, officePos) < 0.3f)
            {
                nearOffice = true;
            }

            if (nearOffice)
            {
                // Coordinated attack logic
                // For example: increase aggression when multiple are nearby
                Debug.Log($"[Teamwork] {leader.characterName} coordinating with {team.Count} others near office!");
            }
        }
        #endregion

        #region Public Methods
        public void ResetAllAnimatronics()
        {
            foreach (var animatronic in animatronics)
            {
                if (animatronic != null)
                {
                    animatronic.ResetAnimatronic();
                }
            }

            UpdateRoomOccupancy();
            Debug.Log("All animatronics reset");
        }

        public Animatronic GetAnimatronicByName(string name)
        {
            return animatronics.Find(a => a != null && a.characterName == name);
        }

        public List<Animatronic> GetActiveAnimatronics()
        {
            return animatronics.FindAll(a => a != null && a.isActive);
        }

        public void SetAllAnimatronicsActive(bool active)
        {
            foreach (var animatronic in animatronics)
            {
                if (animatronic != null)
                {
                    animatronic.isActive = active;
                }
            }
        }
        #endregion

        #region Debug
        [ContextMenu("Print Animatronic Positions")]
        void DebugPrintPositions()
        {
            Debug.Log("=== ANIMATRONIC POSITIONS ===");
            foreach (var animatronic in animatronics)
            {
                if (animatronic != null && animatronic.currentRoom != null)
                {
                    Debug.Log($"{animatronic.characterName}: {animatronic.currentRoom.roomName} (Active: {animatronic.isActive})");
                }
            }
        }

        [ContextMenu("Print Room Occupancy")]
        void DebugPrintOccupancy()
        {
            UpdateRoomOccupancy();
            Debug.Log("=== ROOM OCCUPANCY ===");
            foreach (var kvp in roomOccupancy)
            {
                string animatronicNames = string.Join(", ", kvp.Value.ConvertAll(a => a.characterName));
                Debug.Log($"{kvp.Key.roomName}: {kvp.Value.Count} [{animatronicNames}]");
            }
        }

        [ContextMenu("Reset All Animatronics")]
        void DebugResetAll()
        {
            ResetAllAnimatronics();
        }
        #endregion
    }
}
