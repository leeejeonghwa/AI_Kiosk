using UnityEngine;

public class CharacterControllerBefore : MonoBehaviour
{
    public Animator             m_BodyAni;
    public Animator             m_EyeAni;
    public Animator             m_MouseAni;

    public SkinnedMeshRenderer  m_EyeRendererMaterial;
    public Mesh[]               m_EyeMesh;

    public SkinnedMeshRenderer  m_MouseRendererMaterial;
    public Mesh[]               m_MouseMesh;


    public int m_RandomSet;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if ( Input.GetKeyDown( KeyCode.A ) )
        {
            TestAni( m_RandomSet );
        }
    }

    public void TestAni( int set )
    {
        //body
        m_BodyAni.SetBool( "hi", false );
        m_BodyAni.SetBool( "think", false );
        m_BodyAni.SetBool( "happy", false );
        m_BodyAni.SetBool( "funy", false );
        m_BodyAni.SetBool( "lover", false );
        m_BodyAni.SetBool( "wink", false );
        m_BodyAni.SetBool( "wrong", false );
        m_BodyAni.SetBool( "tell", false );
        m_BodyAni.SetBool( "surprise", false );
        m_BodyAni.SetBool( "error", false );

        //eye
        m_EyeAni.SetBool( "hi", false );
        m_EyeAni.SetBool( "think", false );
        m_EyeAni.SetBool( "happy", false );
        m_EyeAni.SetBool( "funy", false );
        m_EyeAni.SetBool( "lover", false );
        m_EyeAni.SetBool( "wink", false );
        m_EyeAni.SetBool( "wrong", false );
        m_EyeAni.SetBool( "tell", false );
        m_EyeAni.SetBool( "surprise", false );
        m_EyeAni.SetBool( "error", false );

        //mouse
        m_MouseAni.SetBool( "hi", false );
        m_MouseAni.SetBool( "think", false );
        m_MouseAni.SetBool( "happy", false );
        m_MouseAni.SetBool( "funy", false );
        m_MouseAni.SetBool( "lover", false );
        m_MouseAni.SetBool( "wink", false );
        m_MouseAni.SetBool( "wrong", false );
        m_MouseAni.SetBool( "tell", false );
        m_MouseAni.SetBool( "surprise", false );
        m_MouseAni.SetBool( "error", false );

        //m_RandomSet = Random.Range(0, 10);

        switch ( set )
        {
            case 0:
                m_BodyAni.SetBool( "hi", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[0] ;
                m_EyeAni.SetBool( "hi", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[0] ;
                m_MouseAni.SetBool( "hi", true );
                break;

            case 1:
                m_BodyAni.SetBool( "think", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[1];
                m_EyeAni.SetBool( "think", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[1];
                m_MouseAni.SetBool( "think", true );
                break;

            case 2:
                m_BodyAni.SetBool( "happy", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[2];
                m_EyeAni.SetBool( "happy", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[2] ;
                m_MouseAni.SetBool( "happy", true );
                break;

            case 3:
                m_BodyAni.SetBool( "funy", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[3];
                m_EyeAni.SetBool( "funy", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[3] ;
                m_MouseAni.SetBool( "funy", true );
                break;

            case 4:
                m_BodyAni.SetBool( "lover", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[4];
                m_EyeAni.SetBool( "lover", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[4] ;
                m_MouseAni.SetBool( "lover", true );
                break;

            case 5:
                m_BodyAni.SetBool( "wink", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[5];
                m_EyeAni.SetBool( "wink", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[5] ;
                m_MouseAni.SetBool( "wink", true );
                break;

            case 6:
                m_BodyAni.SetBool( "wrong", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[6];
                m_EyeAni.SetBool( "wrong", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[6] ;
                m_MouseAni.SetBool( "wrong", true );
                break;

            case 7:
                m_BodyAni.SetBool( "tell", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[7];
                m_EyeAni.SetBool( "tell", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[7] ;
                m_MouseAni.SetBool( "tell", true );
                break;

            case 8:
                m_BodyAni.SetBool( "surprise", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[8];
                m_EyeAni.SetBool( "surprise", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[8] ;
                m_MouseAni.SetBool( "surprise", true );
                break;

            case 9:
                m_BodyAni.SetBool( "error", true );

                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[9];
                m_EyeAni.SetBool( "error", true );

                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[9] ;
                m_MouseAni.SetBool( "error", true );
                break;

            default:
                Debug.Log( "´ë±â" );
                m_EyeRendererMaterial.sharedMesh = m_EyeMesh[10];
                m_MouseRendererMaterial.sharedMesh = m_MouseMesh[10] ;
                break;
        }
    }
}
