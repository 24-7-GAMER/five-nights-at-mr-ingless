using UnityEngine;
using System.Collections.Generic;

namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// ScriptableObject representing a room in the game
    /// Replaces Python ROOM_GRAPH dictionary
    /// </summary>
    [CreateAssetMenu(fileName = "RoomData", menuName = "Five Nights/Room Data")]
    public class RoomData : ScriptableObject
    {
        [Header("Room Info")]
        public string roomName;
        [TextArea(2, 4)]
        public string description;
        
        [Header("Navigation")]
        public List<RoomData> connectedRooms = new List<RoomData>();
        
        [Header("Minimap")]
        [Range(0f, 1f)]
        public float minimapX = 0.5f; // 0 to 1 (percentage)
        [Range(0f, 1f)]
        public float minimapY = 0.5f; // 0 to 1 (percentage)
        
        [Header("Camera View")]
        public Sprite cameraViewSprite;
        public bool hasCamera = true;
        
        [Header("Special Properties")]
        public bool isOffice = false;
        public bool isStartingRoom = false;
        public bool hasSoundCues = false;
        
        /// <summary>
        /// Get minimap position in screen space
        /// </summary>
        public Vector2 GetMinimapPosition(float screenWidth, float screenHeight)
        {
            return new Vector2(screenWidth * minimapX, screenHeight * minimapY);
        }
        
        /// <summary>
        /// Check if this room is connected to another room
        /// </summary>
        public bool IsConnectedTo(RoomData otherRoom)
        {
            return connectedRooms.Contains(otherRoom);
        }
        
        /// <summary>
        /// Get all neighbor room names
        /// </summary>
        public List<string> GetNeighborNames()
        {
            List<string> names = new List<string>();
            foreach (var room in connectedRooms)
            {
                if (room != null)
                    names.Add(room.roomName);
            }
            return names;
        }
    }
}
