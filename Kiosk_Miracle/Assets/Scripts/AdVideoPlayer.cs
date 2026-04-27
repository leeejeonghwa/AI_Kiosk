using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Video;

public class AdVideoPlayer : MonoBehaviour
{
    public VideoPlayer videoPlayer;
    public RawImage adVideo;
    public RenderTexture adTexture;

    [Header("이미지 슬라이드")]
    public bool useImage = true;
    public RawImage mainImg;
    public RawImage subImg;
    public Texture2D[] adImages;
    public GameObject adImgsArea;
    public float displayTime = 10f;
    public float slideDuration = 0.5f;

    private AspectRatioFitter mainARF;
    private AspectRatioFitter subARF;

    private int currentIdx = 0;
    private Coroutine slideRoutine;
    private Vector2 mainDefaultPos;
    private Vector2 rightPos;
    private Vector2 leftPos;

    void Awake()
    {
        float width = mainImg.rectTransform.rect.width;

        mainDefaultPos = mainImg.rectTransform.anchoredPosition;
        rightPos = mainDefaultPos + new Vector2(width, 0);
        leftPos = mainDefaultPos + new Vector2(-width, 0);

        mainARF = mainImg.GetComponent<AspectRatioFitter>();
        subARF = subImg.GetComponent<AspectRatioFitter>();

        if(mainImg.texture != null) UpdateRatio(mainImg, mainARF);
        if(subImg.texture != null) UpdateRatio(subImg, subARF);
        
        adVideo.gameObject.SetActive(false);
        adImgsArea.SetActive(false);
        subImg.gameObject.SetActive(false);
    }

    public IEnumerator LoadResource(string url)
    {
        if(useImage)
        {
            if(adVideo.gameObject.activeSelf == true)
            {
                adVideo.gameObject.SetActive(false);
            }

            adImgsArea.SetActive(true);

            if(adImages != null && adImages.Length >= 2)
            {
                slideRoutine ??= StartCoroutine(ImageSlideLoop());
            }
            else if(adImages != null && adImages.Length == 1)
            {
                mainImg.texture = adImages[0];
                mainImg.rectTransform.anchoredPosition = mainDefaultPos;
                mainImg.gameObject.SetActive(true);
            }
            yield break;
        }

        if(string.IsNullOrEmpty(url))
        {
            LocalHostUnity.Log.Warn($"영상 url 주소 비어있음");
            yield break;
        }

        if(adImgsArea.activeSelf == true)
        {
            adImgsArea.SetActive(false);
        }

        adVideo.gameObject.SetActive(true);

        if(url.ToLower().EndsWith(".mp4"))
        {
            adVideo.texture = adTexture;
            videoPlayer.url = url;
            videoPlayer.Prepare();

            while(!videoPlayer.isPrepared)
            {
                yield return null;
            }

            videoPlayer.Play();
            LocalHostUnity.Log.Info($"광고 영상 재생 시작 : {url}");
        }
    }

    public void StopVideo()
    {
        if(useImage)
        {
            if(slideRoutine != null)
            {
                StopCoroutine(slideRoutine);
                slideRoutine = null;
                LocalHostUnity.Log.Info("광고 이미지 슬라이드 멈춤");
            }
        }

        if(videoPlayer.isPlaying)
        {
            videoPlayer.Stop();
            LocalHostUnity.Log.Info("광고 영상 멈춤");
        }
    }

    IEnumerator ImageSlideLoop()
    {
        UpdateImageAndRatio(mainImg, mainARF, adImages[0]);
        currentIdx = 0;
        adImgsArea.SetActive(true);

        while(true)
        {
            yield return new WaitForSeconds(displayTime);

            int nextidx = (currentIdx + 1) % adImages.Length;
            UpdateImageAndRatio(subImg, subARF, adImages[nextidx]);

            subImg.rectTransform.anchoredPosition = rightPos;
            subImg.gameObject.SetActive(true);

            yield return StartCoroutine(ExecuteSlide());

            currentIdx = nextidx;
            mainImg.texture = adImages[currentIdx];
            UpdateRatio(mainImg, mainARF);

            mainImg.rectTransform.anchoredPosition = mainDefaultPos;
            subImg.gameObject.SetActive(false);
        }
    }

    IEnumerator ExecuteSlide()
    {
        float elapsed = 0;

        while(elapsed < slideDuration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.SmoothStep(0,1,elapsed / slideDuration);

            mainImg.rectTransform.anchoredPosition = Vector2.Lerp(mainDefaultPos, leftPos, t);
            subImg.rectTransform.anchoredPosition = Vector2.Lerp(rightPos, mainDefaultPos, t);

            yield return null;
        }
    }

    private void UpdateImageAndRatio(RawImage img, AspectRatioFitter arf, Texture2D tex)
    {
        if(img == null || tex == null) return;

        img.texture = tex;
        UpdateRatio(img, arf);
    }

    private void UpdateRatio(RawImage img, AspectRatioFitter arf)
    {
        if(arf != null && img.texture != null)
        {
            arf.aspectRatio = (float)img.texture.width / (float)img.texture.height;
        }
    }    
}
