using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

public class MainController : MonoBehaviour
{
    public CharacterController  m_CharacterController;
    public TcpClientUnity       m_Clinet;

    public GameObject           m_SpeechBubble;
    public TMP_Text             m_SpeechText;

    public enum State
    {
        idle,
        hi,
        think,
        happy,
        funy,
        lover,
        wink,
        wrong,
        tell,
        surprise,
        error
    }
    public State                m_PlayState;
    public bool                 m_StateCheck            = false;

    private Coroutine           m_CurrentCoroutine;
    public float                m_TypingSpeed           = 0.1f;
    private string              m_TellMessage;
    [HideInInspector]
    public bool                 m_NoAni                 = false;

    public GameObject[]         m_Uis;
    public GameObject[]         m_Channels;

    public string               m_IdleMessage;
    public string               m_WinkMessage;
    public string               m_ChannelMessage;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if ( m_StateCheck )
        {
            m_StateCheck = false;
            switch( m_PlayState )
            {
                case State.idle:
                    if ( !m_NoAni )
                    {
                        m_CharacterController.Idle();
                    }

                    if ( m_IdleMessage != null )
                    {
                        if ( m_IdleMessage.Contains( "False" ) )
                        {
                            m_SpeechText.text = "";
                            m_SpeechBubble.SetActive( false );
                        }
                    }
                    
                    break;

                case State.hi:
                    if ( !m_NoAni )
                    {
                        m_Clinet.SendText("[llm]: 안녕하세요 읽어줘");
                        m_CharacterController.Hi();
                    }
                    
                    break;

                case State.tell:
                    if ( !m_NoAni )
                    {
                        m_CharacterController.Tell();
                        ShowDialogue( m_TellMessage );
                    }
                    
                    break;

                case State.lover:

                    m_CharacterController.Lover();
                    break;

                case State.happy:
                    m_CharacterController.Happy();
                    break;

                case State.wink:
                    m_CharacterController.Wink();

                    m_Uis[0].gameObject.SetActive(false);
                    m_Uis[1].gameObject.SetActive(false);
                    m_Uis[2].gameObject.SetActive(false);

                    if ( m_WinkMessage.Contains( "공지사항" ) )
                    {
                        if ( !m_Uis[0].gameObject.activeSelf )
                        {
                            m_Uis[0].gameObject.SetActive( true );
                        }
                    }
                    else if ( m_WinkMessage.Contains( "민원" ) )
                    {
                        if ( !m_Uis[1].gameObject.activeSelf )
                        {
                            m_Uis[1].gameObject.SetActive( true );
                        }
                    }
                    else if ( m_WinkMessage.Contains( "안내" ) )
                    {
                        if ( !m_Uis[2].gameObject.activeSelf )
                        {
                            m_Uis[2].gameObject.SetActive( true );
                        }

                        for ( int i = 0; i < m_Channels.Length; i++ )
                        {
                            m_Channels[i].gameObject.SetActive( false );
                        }

                        if ( m_WinkMessage.Contains( "101" ) )
                        {
                            m_Channels[0].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "102" ) )
                        {
                            m_Channels[1].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "103" ) )
                        {
                            m_Channels[2].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "104" ) )
                        {
                            m_Channels[3].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "105" ) )
                        {
                            m_Channels[4].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "106" ) )
                        {
                            m_Channels[5].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "107" ) )
                        {
                            m_Channels[6].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "108" ) )
                        {
                            m_Channels[7].gameObject.SetActive( true );
                        }
                        else if ( m_WinkMessage.Contains( "공원" ) )
                        {
                            m_Channels[8].gameObject.SetActive( true );
                        }
                    }
                    break;
            }
        }

        if ( Input.GetKeyDown( KeyCode.F1 ) )
        {
            m_CharacterController.Hi();
        }

        if ( Input.GetKeyDown( KeyCode.F2 ) )
        {
            m_CharacterController.Think();
        }

        if ( Input.GetKeyDown( KeyCode.F3 ) )
        {
            m_CharacterController.Happy();
        }

        if ( Input.GetKeyDown( KeyCode.F4 ) )
        {
            m_CharacterController.Funy();
        }

        if ( Input.GetKeyDown( KeyCode.F5 ) )
        {
            m_CharacterController.Lover();
        }

        if ( Input.GetKeyDown( KeyCode.F6 ) )
        {
            m_CharacterController.Wink();
        }

        if ( Input.GetKeyDown( KeyCode.F7 ) )
        {
            m_CharacterController.Wrong();
        }

        if ( Input.GetKeyDown( KeyCode.F8 ) )
        {
            m_CharacterController.Surprise();
        }

        if ( Input.GetKeyDown( KeyCode.F9 ) )
        {
            m_CharacterController.Error();
        }
    }

    public void Speech( string str )
    {
        m_SpeechBubble.SetActive( true );
    }

    public void DataClassification( string str )
    {
        if ( str.Contains( "enter" ) )
        {
            //카메라 인식 On
            //m_CharacterController.Hi();
            m_StateCheck = true;
            m_PlayState = State.hi;
        }
        else if ( str.Contains( "remove" ) )
        {
            //카메라 인식 Off
            //m_CharacterController.Idle();
            //Debug.Log( "Test2" );
            m_StateCheck = true;
            m_PlayState = State.idle;
        }
        else if ( str.Contains( "complete" ) )
        {
            m_StateCheck = true;
            m_PlayState = State.idle;

            m_IdleMessage = str;
        }
        else if (str.Contains("STT"))
        {
            // 유저 소리 등록
            if (str.Contains("사랑") || str.Contains("즐거"))
            {
                m_StateCheck = true;
                m_PlayState = State.lover;
                m_NoAni = true;
            }
            else if (str.Contains("고마워") || str.Contains("행복"))
            {
                m_StateCheck = true;
                m_PlayState = State.happy;
                m_NoAni = true;
            }
            else if (str.Contains("안내") || str.Contains("민원") || str.Contains("공지사항")
                || str.Contains("알려") || str.Contains("보여") || str.Contains("가는")
                || str.Contains("닫아") || str.Contains("처음"))
            {
                m_StateCheck = true;
                m_PlayState = State.wink;
                m_NoAni = true;

                m_WinkMessage = str;

            }
        }
        else if (str.Contains("llm"))
        {
            if (!m_NoAni)
            {
                m_StateCheck = true;
                m_PlayState = State.tell;
                m_TellMessage = str.Substring(str.IndexOf(':') + 1);
            }
        }
    }

    public void ShowDialogue(string message)
    {
        if ( m_CurrentCoroutine != null )
            StopCoroutine( m_CurrentCoroutine );

        m_CurrentCoroutine = StartCoroutine( TypeSentence( message ) );
    }

    private IEnumerator TypeSentence(string message)
    {
        m_SpeechText.text = "";
        m_SpeechBubble.SetActive( true );
        foreach (char c in message)
        {
            m_SpeechText.text += c;
            yield return new WaitForSeconds(m_TypingSpeed);
        }

        yield return new WaitForSeconds(2f); // 잠시 대기 후
        m_SpeechBubble.SetActive(false); // 말풍선 숨김
        m_CharacterController.Idle();
    }

    public void UiActiveOnSetting( int i )
    {
        m_Uis[i].gameObject.SetActive( true );
    }

    public void UiActiveOffSetting( int i )
    {
        m_Uis[i].gameObject.SetActive( false );

        if ( i == 2 )
        {
            ChannelUIOffSetting();
        }
    }

    public void ChannelUIOnSetting( int index )
    {
        for ( int i = 0; i < m_Channels.Length; i++ )
        {
            m_Channels[i].gameObject.SetActive( false );
        }

        m_Channels[index].gameObject.SetActive( true );
    }

    public void ChannelUIOffSetting ()
    {
        for ( int i = 0; i < m_Channels.Length; i++ )
        {
            m_Channels[i].gameObject.SetActive( false );
        }

    }

    public void Stopllm()
    {
        m_Clinet.SendData( "[TTS]:Stop" );
    }
}
