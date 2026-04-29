using System;
using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class ServerStatus
{
    public string current_state; // JS의 data.current_state
    public string session_id;    // JS의 data.session_id
    public string message_text;  // JS의 data.message_text (GREETING, RESPONDING 시 내용)
    public string user_text;     // JS의 data.user_text (PROCESSING 시 사용자가 말한 내용)
    public bool   is_speaking;   // TTS 재생 중 여부
    public string speaking_text; // 현재 TTS가 말하는 텍스트
}

public class LocalHostUnity : MonoBehaviour
{
    [Header("서버 세팅")]
    public string baseURL = "http://127.0.0.1:8000";
    public string adVideoURL;
    public float pollInterval = 0.5f; // JS와 동일하게 0.5초

    [Header("UI 요소")]
    public GameObject adScreen;
    public GameObject mainScreen;
    public TMP_Text aiText;             // 메인 메시지 표시용

    [Header("자막")]
    public GameObject subtitleObject;   // 자막 패널 GameObject (Inspector에서 연결)
    public TMP_Text subtitleText;       // 자막 텍스트 (Inspector에서 연결)

    private string lastState = null;
    private string lastSpeakingText = null;
    public CharacterController characterController;
    public AdVideoPlayer adVideoPlayer;
    
    void Start()
    {
        StartCoroutine(StatusPollingLoop());
    }

    void Update()
    {
        if(Input.GetKeyDown(KeyCode.F1))
        {
            Log.Info("Debug : F1 눌림 - 광고 화면(idle)로 강제 전환");
            ForceStateReset("IDLE");
        }

        if(Input.GetKeyDown(KeyCode.F2))
        {
            Log.Info("Debug : F2 눌림 - 메인 화면으로 강제 전환");
            ForceStateReset("USER_DETECTED");
        }
    }

    IEnumerator StatusPollingLoop()
    {
        while (true)
        {
            // JS의 fetch('/api/state')와 동일한 경로
            using (UnityWebRequest request = UnityWebRequest.Get($"{baseURL}/api/state"))
            {
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    ServerStatus data = JsonUtility.FromJson<ServerStatus>(request.downloadHandler.text);

                    // 상태 변화 처리
                    if (data.current_state != lastState)
                    {
                        HandleStateChange(data.current_state, data);
                        lastState = data.current_state;
                    }

                    // 자막 처리 (speaking_text 변화 감지)
                    if (data.speaking_text != lastSpeakingText)
                    {
                        UpdateSubtitle(data.is_speaking, data.speaking_text);
                        lastSpeakingText = data.speaking_text;
                    }
                }
                else
                {
                    Log.Error($"서버 연결 실패: {request.error}");
                }
            }
            yield return new WaitForSeconds(pollInterval);
        }
    }

    void HandleStateChange(string state, ServerStatus data)
    {
        Log.Info($"상태 변경: {state}");

        if(state != "IDLE" || state == "USER_DETECTED")
        {
            if(adScreen.activeSelf) adScreen.SetActive(false);
            if(!mainScreen.activeSelf) mainScreen.SetActive(true);

            StartCoroutine(adVideoPlayer.LoadResource(adVideoURL));
        }
        else
        {
            adVideoPlayer.StopVideo();
        }

        switch (state)
        {
            case "IDLE":
                adScreen.SetActive(true);
                mainScreen.SetActive(false);
                aiText.text = "";
                break;
            
            case "USER_DETECTED":
                characterController.Idle();
                break;

            case "GREETING":
                aiText.text = data.message_text ?? "안녕하세요!";
                characterController.Hi();
                break;

            case "LISTENING":
                characterController.Idle(); // 혹은 Listen 애니메이션
                break;

            case "PROCESSING":
                // JS: data.user_text ? `"${data.user_text}"` : '';
                aiText.text = !string.IsNullOrEmpty(data.user_text) ? $"\"{data.user_text}\"" : "";
                characterController.Think();
                break;

            case "RESPONDING":
                aiText.text = data.message_text;
                characterController.Tell();
                break;

            default:
                Log.Warn($"알 수 없는 상태: {state}");
                break;
        }
    }

    void UpdateSubtitle(bool isSpeaking, string text)
    {
        if (subtitleObject == null || subtitleText == null) return;

        if (isSpeaking && !string.IsNullOrEmpty(text))
        {
            subtitleText.text = text;
            subtitleObject.SetActive(true);
        }
        else
        {
            subtitleObject.SetActive(false);
            subtitleText.text = "";
        }
    }

    // --- API 요청 함수들 (JS의 sendDetection, startListening 등) ---

    public void RequestDetection() => StartCoroutine(PostRequest("/api/detection", "{\"detected\": true}"));
    public void RequestGreeting() => StartCoroutine(PostRequest("/api/greeting", ""));
    public void RequestReset() => StartCoroutine(PostRequest("/api/session/reset", ""));

    IEnumerator PostRequest(string path, string jsonBody)
    {
        using (UnityWebRequest request = new UnityWebRequest($"{baseURL}{path}", "POST"))
        {
            if (!string.IsNullOrEmpty(jsonBody))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonBody);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            }
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();
            // 요청 후 즉시 상태 갱신 (JS의 fetchState() 호출과 동일)
            // 바로 다음 루프에서 처리되므로 생략 가능하나 즉각 반응을 위해 필요시 코루틴 재호출
        }
    }

    public static class Log
    {
        private static string TimeTag => $"[{DateTime.Now:HH:mm:ss}]";

        public static void Info(object msg)
        {
            Debug.Log(TimeTag+msg);
        }

        public static void Warn(object msg)
        {
            Debug.LogWarning(TimeTag+msg);
        }

        public static void Error(object msg)
        {
            Debug.LogError(TimeTag+msg);
        }
    }

    private void ForceStateReset(string targetState)
    {
        StopAllCoroutines();
        adVideoPlayer.StopVideo();

        RequestReset();

        if(targetState == "IDLE")
        {
            adScreen.SetActive(true);
            mainScreen.SetActive(false);
            aiText.text = "";
            characterController.Idle();
        }
        else if(targetState == "USER_DETECTED")
        {
            adScreen.SetActive(false);
            mainScreen.SetActive(true);
            characterController.Idle();
            StartCoroutine(adVideoPlayer.LoadResource(adVideoURL));
        }

        StartCoroutine(StatusPollingLoop());
    }
}