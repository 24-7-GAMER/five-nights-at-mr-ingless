namespace FiveNightsAtMrIngles
{
    /// <summary>
    /// Global constants for the game
    /// Converted from Python CONSTANTS section
    /// </summary>
    public static class Constants
    {
        // Window Settings
        public const int WINDOW_WIDTH = 1280;
        public const int WINDOW_HEIGHT = 720;
        public const string WINDOW_TITLE = "Five Nights at Mr Ingles's";
        public const int TARGET_FPS = 60;

        // Performance Optimization
        public const int MAX_PARTICLE_CACHE_SIZE = 100;
        public const int MAX_OVERLAY_CACHE_SIZE = 200;
        public const float MIN_CHROMATIC_ABERRATION = 0.5f;
        public const int SCREEN_GLOW_CIRCLE_INTERVAL = 60;
        public const float VHS_GLITCH_FREQUENCY = 0.02f;
        public const int SCANLINE_SPACING = 12;
        public const int STATIC_PARTICLE_COUNT_MULTIPLIER = 20;
        public const int CAMERA_NOISE_PARTICLE_COUNT = 8;
        public const int MAX_PARTICLES = 100;
        public const int PARTICLE_UPDATE_SKIP = 1;
        public const float EFFECTS_QUALITY = 0.6f;

        // Gameplay Constants
        public const int MAX_NIGHTS = 5;
        public const int HOURS_PER_NIGHT = 6; // 12 AM to 6 AM
        
        // Save File
        public const string SAVE_FILE_NAME = "mr_ingles_save.json";
    }
}
