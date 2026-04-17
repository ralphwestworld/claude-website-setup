using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;

namespace VRFramework.Core
{
    /// <summary>
    /// Screen-space fade used between scene transitions. Attach to a Canvas
    /// rendered in Screen Space - Camera on the VR head camera, with a
    /// full-screen black Image assigned to <see cref="fadeImage"/>.
    /// </summary>
    public class SceneTransition : MonoBehaviour
    {
        [SerializeField] private Image fadeImage;
        [SerializeField] private CanvasGroup canvasGroup;

        private void Awake()
        {
            if (canvasGroup == null && fadeImage != null)
                canvasGroup = fadeImage.GetComponentInParent<CanvasGroup>();
            if (canvasGroup != null) canvasGroup.alpha = 0f;
        }

        public Task FadeOutAsync(float seconds) => FadeAsync(0f, 1f, seconds);
        public Task FadeInAsync(float seconds)  => FadeAsync(1f, 0f, seconds);

        private async Task FadeAsync(float from, float to, float seconds)
        {
            if (canvasGroup == null) return;
            float t = 0f;
            seconds = Mathf.Max(0.001f, seconds);
            canvasGroup.blocksRaycasts = true;
            while (t < seconds)
            {
                t += Time.unscaledDeltaTime;
                canvasGroup.alpha = Mathf.Lerp(from, to, t / seconds);
                await Task.Yield();
            }
            canvasGroup.alpha = to;
            canvasGroup.blocksRaycasts = to > 0.01f;
        }
    }
}
