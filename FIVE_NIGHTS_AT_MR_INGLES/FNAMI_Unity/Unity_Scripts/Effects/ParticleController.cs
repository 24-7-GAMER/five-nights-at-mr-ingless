using UnityEngine;
using System.Collections.Generic;

namespace FiveNightsAtMrIngles.Effects
{
    /// <summary>
    /// Manages particle effects with object pooling
    /// </summary>
    public class ParticleController : MonoBehaviour
    {
        #region Singleton
        public static ParticleController Instance { get; private set; }

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

        #region Particle Prefabs
        [Header("Particle Prefabs")]
        public GameObject staticParticlePrefab;
        public GameObject dustParticlePrefab;
        public GameObject sparkParticlePrefab;
        public GameObject glowParticlePrefab;
        public GameObject smokeParticlePrefab;

        [Header("Pool Settings")]
        public int initialPoolSize = 50;
        public int maxParticles = 100;
        #endregion

        #region Private Fields
        private Dictionary<string, Queue<GameObject>> particlePools = new Dictionary<string, Queue<GameObject>>();
        private List<GameObject> activeParticles = new List<GameObject>();
        private int totalParticlesSpawned = 0;
        #endregion

        #region Unity Lifecycle
        void Start()
        {
            InitializePools();
        }

        void Update()
        {
            CleanupInactiveParticles();
        }
        #endregion

        #region Initialization
        void InitializePools()
        {
            CreatePool("static", staticParticlePrefab, initialPoolSize / 5);
            CreatePool("dust", dustParticlePrefab, initialPoolSize / 5);
            CreatePool("spark", sparkParticlePrefab, initialPoolSize / 5);
            CreatePool("glow", glowParticlePrefab, initialPoolSize / 5);
            CreatePool("smoke", smokeParticlePrefab, initialPoolSize / 5);

            Debug.Log($"ParticleController initialized {particlePools.Count} pools");
        }

        void CreatePool(string poolName, GameObject prefab, int size)
        {
            if (prefab == null)
            {
                Debug.LogWarning($"Prefab for pool '{poolName}' is null, skipping");
                return;
            }

            Queue<GameObject> pool = new Queue<GameObject>();

            for (int i = 0; i < size; i++)
            {
                GameObject obj = Instantiate(prefab, transform);
                obj.SetActive(false);
                pool.Enqueue(obj);
            }

            particlePools[poolName] = pool;
        }
        #endregion

        #region Particle Spawning
        public GameObject SpawnParticle(string type, Vector3 position, Quaternion rotation)
        {
            if (totalParticlesSpawned >= maxParticles)
            {
                // Limit reached, remove oldest particle
                RecycleOldestParticle();
            }

            GameObject particle = GetFromPool(type);
            if (particle == null)
                return null;

            particle.transform.position = position;
            particle.transform.rotation = rotation;
            particle.SetActive(true);

            activeParticles.Add(particle);
            totalParticlesSpawned++;

            // Auto-return to pool after particle system finishes
            ParticleSystem ps = particle.GetComponent<ParticleSystem>();
            if (ps != null)
            {
                StartCoroutine(ReturnToPoolAfterTime(type, particle, ps.main.duration));
            }

            return particle;
        }

        public void SpawnStaticBurst(Vector3 position, int count = 10)
        {
            for (int i = 0; i < count; i++)
            {
                Vector3 randomOffset = Random.insideUnitSphere * 2f;
                SpawnParticle("static", position + randomOffset, Quaternion.identity);
            }
        }

        public void SpawnDustCloud(Vector3 position, float radius = 1f)
        {
            int count = Random.Range(5, 15);
            for (int i = 0; i < count; i++)
            {
                Vector3 randomPos = position + Random.insideUnitSphere * radius;
                SpawnParticle("dust", randomPos, Quaternion.identity);
            }
        }

        public void SpawnSparks(Vector3 position, int count = 5)
        {
            for (int i = 0; i < count; i++)
            {
                Vector3 randomOffset = Random.insideUnitSphere * 0.5f;
                SpawnParticle("spark", position + randomOffset, Quaternion.identity);
            }
        }
        #endregion

        #region Object Pooling
        GameObject GetFromPool(string poolName)
        {
            if (!particlePools.ContainsKey(poolName))
            {
                Debug.LogWarning($"Pool '{poolName}' does not exist");
                return null;
            }

            Queue<GameObject> pool = particlePools[poolName];

            if (pool.Count > 0)
            {
                return pool.Dequeue();
            }
            else
            {
                // Pool empty, create new instance
                GameObject prefab = GetPrefabForPool(poolName);
                if (prefab != null)
                {
                    GameObject newObj = Instantiate(prefab, transform);
                    return newObj;
                }
            }

            return null;
        }

        void ReturnToPool(string poolName, GameObject obj)
        {
            if (obj == null)
                return;

            obj.SetActive(false);
            activeParticles.Remove(obj);
            totalParticlesSpawned--;

            if (particlePools.ContainsKey(poolName))
            {
                particlePools[poolName].Enqueue(obj);
            }
            else
            {
                Destroy(obj);
            }
        }

        GameObject GetPrefabForPool(string poolName)
        {
            switch (poolName.ToLower())
            {
                case "static": return staticParticlePrefab;
                case "dust": return dustParticlePrefab;
                case "spark": return sparkParticlePrefab;
                case "glow": return glowParticlePrefab;
                case "smoke": return smokeParticlePrefab;
                default: return null;
            }
        }

        System.Collections.IEnumerator ReturnToPoolAfterTime(string poolName, GameObject particle, float delay)
        {
            yield return new WaitForSeconds(delay);
            ReturnToPool(poolName, particle);
        }
        #endregion

        #region Cleanup
        void CleanupInactiveParticles()
        {
            // Remove particles that have finished playing
            for (int i = activeParticles.Count - 1; i >= 0; i--)
            {
                if (activeParticles[i] == null || !activeParticles[i].activeInHierarchy)
                {
                    activeParticles.RemoveAt(i);
                    totalParticlesSpawned--;
                }
            }
        }

        void RecycleOldestParticle()
        {
            if (activeParticles.Count > 0)
            {
                GameObject oldest = activeParticles[0];
                activeParticles.RemoveAt(0);

                if (oldest != null)
                {
                    oldest.SetActive(false);
                    totalParticlesSpawned--;
                }
            }
        }

        public void ClearAllParticles()
        {
            foreach (var particle in activeParticles)
            {
                if (particle != null)
                {
                    particle.SetActive(false);
                }
            }

            activeParticles.Clear();
            totalParticlesSpawned = 0;
        }
        #endregion

        #region Debug
        [ContextMenu("Test Static Burst")]
        void TestStaticBurst()
        {
            if (Camera.main != null)
            {
                SpawnStaticBurst(Camera.main.transform.position + Vector3.forward * 5f, 20);
            }
        }

        [ContextMenu("Test Dust Cloud")]
        void TestDustCloud()
        {
            if (Camera.main != null)
            {
                SpawnDustCloud(Camera.main.transform.position + Vector3.forward * 5f);
            }
        }

        [ContextMenu("Test Sparks")]
        void TestSparks()
        {
            if (Camera.main != null)
            {
                SpawnSparks(Camera.main.transform.position + Vector3.forward * 5f, 10);
            }
        }

        [ContextMenu("Clear All Particles")]
        void DebugClearAll()
        {
            ClearAllParticles();
        }

        [ContextMenu("Print Pool Status")]
        void PrintPoolStatus()
        {
            Debug.Log("=== PARTICLE POOL STATUS ===");
            Debug.Log($"Active Particles: {activeParticles.Count}/{maxParticles}");
            foreach (var kvp in particlePools)
            {
                Debug.Log($"{kvp.Key}: {kvp.Value.Count} available");
            }
        }
        #endregion
    }
}
