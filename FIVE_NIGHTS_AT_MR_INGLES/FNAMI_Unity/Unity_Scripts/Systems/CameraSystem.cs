using UnityEngine;
using System.Collections.Generic;
using System;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Manages camera system and room viewing
    /// Converted from Python CameraSystem class
    /// </summary>
    public class CameraSystem : MonoBehaviour
    {
        #region Singleton
        public static CameraSystem Instance { get; private set; }

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
        [Header("Room Database")]
        public List<RoomData> allRooms = new List<RoomData>();
        
        [Header("Current State")]
        public int currentCameraIndex = 0;
        #endregion

        #region Events
        public static event Action<RoomData> OnCameraSwitch;
        public static event Action<RoomData, RoomData> OnCameraChange; // (from, to)
        #endregion

        #region Camera Control
        public void SwitchCamera(int index)
        {
            if (index < 0 || index >= allRooms.Count)
            {
                Debug.LogWarning($"Invalid camera index: {index}");
                return;
            }
            
            if (index == currentCameraIndex)
                return;
            
            RoomData previousRoom = GetCurrentRoom();
            currentCameraIndex = index;
            RoomData newRoom = GetCurrentRoom();
            
            Debug.Log($"Camera switched to: {newRoom.roomName}");
            
            OnCameraSwitch?.Invoke(newRoom);
            OnCameraChange?.Invoke(previousRoom, newRoom);
        }

        public void NextCamera()
        {
            int newIndex = (currentCameraIndex + 1) % allRooms.Count;
            SwitchCamera(newIndex);
        }

        public void PreviousCamera()
        {
            int newIndex = currentCameraIndex - 1;
            if (newIndex < 0)
                newIndex = allRooms.Count - 1;
            SwitchCamera(newIndex);
        }

        public void SwitchToRoom(string roomName)
        {
            for (int i = 0; i < allRooms.Count; i++)
            {
                if (allRooms[i].roomName == roomName)
                {
                    SwitchCamera(i);
                    return;
                }
            }
            
            Debug.LogWarning($"Room not found: {roomName}");
        }

        public RoomData GetCurrentRoom()
        {
            if (currentCameraIndex >= 0 && currentCameraIndex < allRooms.Count)
                return allRooms[currentCameraIndex];
            
            return null;
        }

        public string GetCurrentRoomName()
        {
            RoomData room = GetCurrentRoom();
            return room != null ? room.roomName : "Unknown";
        }
        #endregion

        #region Unity Lifecycle
        void Start()
        {
            InitializeRooms();
        }
        #endregion

        #region Room Queries
        public RoomData GetRoomByName(string roomName)
        {
            return allRooms.Find(r => r.roomName == roomName);
        }

        public int GetRoomIndex(string roomName)
        {
            return allRooms.FindIndex(r => r.roomName == roomName);
        }

        public List<string> GetAllRoomNames()
        {
            List<string> names = new List<string>();
            foreach (var room in allRooms)
            {
                if (room != null)
                    names.Add(room.roomName);
            }
            return names;
        }
        #endregion

        #region Initialization
        public void InitializeRooms()
        {
            if (allRooms.Count == 0)
            {
                Debug.LogWarning("No rooms assigned to CameraSystem!");
                return;
            }
            
            // Find starting room (usually Stage or first room)
            int startIndex = allRooms.FindIndex(r => r.isStartingRoom);
            if (startIndex >= 0)
            {
                currentCameraIndex = startIndex;
            }
            else
            {
                currentCameraIndex = 0;
            }
            
            Debug.Log($"Camera system initialized with {allRooms.Count} rooms. Starting at: {GetCurrentRoomName()}");
        }
        #endregion

        #region Debug
        [ContextMenu("Print All Rooms")]
        void DebugPrintRooms()
        {
            Debug.Log($"Total rooms: {allRooms.Count}");
            for (int i = 0; i < allRooms.Count; i++)
            {
                if (allRooms[i] != null)
                {
                    Debug.Log($"[{i}] {allRooms[i].roomName} - Connections: {allRooms[i].connectedRooms.Count}");
                }
            }
        }

        [ContextMenu("Next Camera")]
        void DebugNextCamera()
        {
            NextCamera();
        }

        [ContextMenu("Previous Camera")]
        void DebugPreviousCamera()
        {
            PreviousCamera();
        }
        #endregion
    }
}
