using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class TcpClientUnity : MonoBehaviour
{
    public MainController m_Main;

    private TcpClient client;
    private NetworkStream stream;
    private Thread receiveThread;
    private bool isConnected = false;

    public string serverIp = "127.0.0.1";
    public int serverPort = 9001;

    void Start()
    {
        ConnectToServer();
    }

    void ConnectToServer()
    {
        try
        {
            client = new TcpClient();
            client.Connect(serverIp, serverPort);
            stream = client.GetStream();
            isConnected = true;

            Debug.Log($"[클라이언트] 서버 {serverIp}:{serverPort}에 연결됨");

            // 서버에 초기 메시지 전송
            SendData("oh hiyo agent");
            Debug.Log( "SendData 호출 완료" );

            // 수신 스레드 시작
            receiveThread = new Thread(ReceiveData);
            receiveThread.IsBackground = true;
            receiveThread.Start();
        }
        catch (Exception e)
        {
            Debug.LogError("[클라이언트] 서버 연결 실패: " + e.Message);
        }
    }

    void ReceiveData()
    {
        byte[] buffer = new byte[1024];

        try
        {
            while (isConnected)
            {
                int bytes = stream.Read(buffer, 0, buffer.Length);
                if (bytes == 0)
                {
                    Debug.LogWarning("[클라이언트] 서버 연결이 끊어졌습니다.");
                    break;
                }

                string message = Encoding.UTF8.GetString(buffer, 0, bytes);
                Debug.Log("[서버] " + message);
                m_Main.DataClassification( message );
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning("[클라이언트] 수신 오류: " + e.Message);
        }
    }

    public void SendData(string message)
    {
        if (client == null || !client.Connected || stream == null)
            return;

        try
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            stream.Write(data, 0, data.Length);
        }
        catch (Exception e)
        {
            Debug.LogWarning("[클라이언트] 전송 오류: " + e.Message);
        }
    }

    public void SendText(string message)
    {
        if (stream != null && stream.CanWrite)
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            try
            {
                stream.Write(data, 0, data.Length);
                Debug.Log($"[보냄] {message}");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[전송 오류] {e.Message}");
            }
        }
    }

    void OnApplicationQuit()
    {
        try
        {
            isConnected = false;
            stream?.Close();
            client?.Close();
            receiveThread?.Abort();
            Debug.Log("[클라이언트] 연결 종료");
        }
        catch { }
    }

    // 테스트용: 키 입력으로 메시지 보내기
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Return))
        {
            SendData("Hello from Unity");
        }

        if ( Input.GetKeyDown( KeyCode.Escape ) )
        {
            SendData("quit");
            OnApplicationQuit();
        }

        if ( Input.GetKeyDown( KeyCode.A ) )
        {
            SendText( "[llm]: 회사 정보 알려줘" );
        }

        if ( Input.GetKeyDown( KeyCode.D ) )
        {
            SendText( "[TTS]:Stop" );
        }
        if ( Input.GetKeyDown( KeyCode.S ) )
        {
            SendText( "Stop" );
        }

        if ( Input.GetKeyDown( KeyCode.Z ) )
        {
            SendText( "[llm]: 안녕하세요 읽어줘" );
        }
    }
}
