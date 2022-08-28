/* Imports */

var L8 = ee.ImageCollection("LANDSAT/LC08/C01/T1"),
    ROI = 
    /* color: #d63000 */
    /* shown: false */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[22.372772219705222, 39.681758480649094],
          [22.372772219705222, 39.45097258269616],
          [23.139068606423972, 39.45097258269616],
          [23.139068606423972, 39.681758480649094]]], null, false),
    Rural2 = 
    /* color: #0b4a8b */
    /* shown: false */
    ee.Geometry.Polygon(
        [[[22.40611926344427, 39.48599890763816],
          [22.464160414427106, 39.52653789906045],
          [22.42981413741626, 39.52918880471507]]]),
    Rural3 = 
    /* color: #ffc82d */
    /* shown: false */
    ee.Geometry.Polygon(
        [[[22.53310426687313, 39.62945123055527],
          [22.603634318686996, 39.61540577738784],
          [22.564412739194818, 39.66389034775857]]]),
    Rural4 = 
    /* color: #00ffff */
    /* shown: false */
    ee.Geometry.Polygon(
        [[[22.545814166209556, 39.55064705652064],
          [22.555419420855728, 39.53127312783795],
          [22.629016752153237, 39.527844617406544],
          [22.579507804445775, 39.56125029371498]]]),
    Rural1 = 
    /* color: #bf04c2 */
    /* shown: false */
    ee.Geometry.Polygon(
        [[[22.69005827501482, 39.538715398084115],
          [22.716149651050326, 39.49634121489468],
          [22.784125315018873, 39.53024257558337],
          [22.711343112164204, 39.547187250943416]]]),
    forest = 
    /* color: #0aff00 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([23.019851999273335, 39.497277020342864]),
            {
              "class": 0,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([23.05693085669521, 39.50363496926972]),
            {
              "class": 0,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([23.058990793218648, 39.473959565348345]),
            {
              "class": 0,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.973846750249898, 39.493038064620336]),
            {
              "class": 0,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.938141183843648, 39.52376463707104]),
            {
              "class": 0,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.91685517310146, 39.52482393169754]),
            {
              "class": 0,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.973160104742085, 39.52641284334069]),
            {
              "class": 0,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.939514474859273, 39.547594857719886]),
            {
              "class": 0,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.813171701421773, 39.59787623264804]),
            {
              "class": 0,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.83171113013271, 39.62062318031391]),
            {
              "class": 0,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.87016327857021, 39.63172943851223]),
            {
              "class": 0,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.846817331304585, 39.6010506739803]),
            {
              "class": 0,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.861236886968648, 39.62855640378777]),
            {
              "class": 0,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.827591257085835, 39.5952307537292]),
            {
              "class": 0,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.80699189185146, 39.58306024938301]),
            {
              "class": 0,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.80699189185146, 39.57882652937197]),
            {
              "class": 0,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.78776581763271, 39.59999254303582]),
            {
              "class": 0,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.822098093023335, 39.629085253014445]),
            {
              "class": 0,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.859863595953023, 39.62220989776862]),
            {
              "class": 0,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.860550241460835, 39.60951513953513]),
            {
              "class": 0,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([23.012298898687398, 39.486149210295835]),
            {
              "class": 0,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([23.064483957281148, 39.45540600698518]),
            {
              "class": 0,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([23.088516550054585, 39.46123765832545]),
            {
              "class": 0,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.849306421270406, 39.65122718540198]),
            {
              "class": 0,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.879518823614156, 39.65122718540198]),
            {
              "class": 0,
              "system:index": "24"
            })]),
    rural = 
    /* color: #a4ff04 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.718414621343648, 39.53753420684552]),
            {
              "class": 1,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.72184784888271, 39.53144415702513]),
            {
              "class": 1,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.70914490698818, 39.521116329813566]),
            {
              "class": 1,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.682022409429585, 39.54574168951368]),
            {
              "class": 1,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.69060547827724, 39.57009366506873]),
            {
              "class": 1,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.675842599859273, 39.584118638974815]),
            {
              "class": 1,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.657989816656148, 39.584118638974815]),
            {
              "class": 1,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.707428293218648, 39.54018188794941]),
            {
              "class": 1,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.699188547124898, 39.52932575359423]),
            {
              "class": 1,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.631897287359273, 39.578297296185916]),
            {
              "class": 1,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.728027658453023, 39.495687442237404]),
            {
              "class": 1,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.748627023687398, 39.468924088601305]),
            {
              "class": 1,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.58554871558193, 39.54574168951368]),
            {
              "class": 1,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.62125428198818, 39.52667765841326]),
            {
              "class": 1,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.624344186773335, 39.55580115056789]),
            {
              "class": 1,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.668289499273335, 39.56215374288633]),
            {
              "class": 1,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.646316843023335, 39.57062296088859]),
            {
              "class": 1,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.690691308965718, 39.55705848064535]),
            {
              "class": 1,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.676271753301656, 39.54594024561733]),
            {
              "class": 1,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.679704980840718, 39.56923355074325]),
            {
              "class": 1,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.652239160528218, 39.60786200491498]),
            {
              "class": 1,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.607607202520406, 39.61103598852484]),
            {
              "class": 1,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.597307519903218, 39.62637485799897]),
            {
              "class": 1,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.588381128301656, 39.62531711406956]),
            {
              "class": 1,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.642626123418843, 39.6089200156189]),
            {
              "class": 1,
              "system:index": "24"
            })]),
    urban = 
    /* color: #ff0904 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.405647592535054, 39.62062318031391]),
            {
              "class": 2,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.42075379370693, 39.62220989776862]),
            {
              "class": 2,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.409424142828023, 39.61506938273889]),
            {
              "class": 2,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.398437814703023, 39.62300324285364]),
            {
              "class": 2,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.40152771948818, 39.63595992510154]),
            {
              "class": 2,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.46813233374599, 39.56665314374649]),
            {
              "class": 2,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.466759042730367, 39.56162438241584]),
            {
              "class": 2,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.462295846929585, 39.56268309931626]),
            {
              "class": 2,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.434830026617085, 39.62696983185367]),
            {
              "class": 2,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.403587656011617, 39.632787084414424]),
            {
              "class": 2,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.41594727515224, 39.62194544738584]),
            {
              "class": 2,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.466072397222554, 39.560565649353265]),
            {
              "class": 2,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.40904523567169, 39.62938513313516]),
            {
              "class": 2,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.412650124587707, 39.628327435223824]),
            {
              "class": 2,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.4123068018338, 39.63169879094395]),
            {
              "class": 2,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.41531087593048, 39.63024450078208]),
            {
              "class": 2,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.426468865432433, 39.63249202723792]),
            {
              "class": 2,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.429644600906066, 39.63678856576294]),
            {
              "class": 2,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.428357140578917, 39.64128312043339]),
            {
              "class": 2,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.426640526809386, 39.64101874294982]),
            {
              "class": 2,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.423207299270324, 39.64174577859771]),
            {
              "class": 2,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.416684166946105, 39.63116996169492]),
            {
              "class": 2,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.410504357375792, 39.6276002585303]),
            {
              "class": 2,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.414109246291808, 39.626806966148365]),
            {
              "class": 2,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.418486611404113, 39.63064112840346]),
            {
              "class": 2,
              "system:index": "24"
            })]),
    sea = 
    /* color: #190699 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.962002773817243, 39.6567655547734]),
            {
              "class": 3,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.96131612830943, 39.59912026338841]),
            {
              "class": 3,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.929730434950056, 39.62715562405966]),
            {
              "class": 3,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.930417080457868, 39.64989295081309]),
            {
              "class": 3,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.99427511268443, 39.60176559375436]),
            {
              "class": 3,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([23.023800869520368, 39.57530774355931]),
            {
              "class": 3,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([23.049893398817243, 39.57795398321098]),
            {
              "class": 3,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([23.056073208387556, 39.61128794644237]),
            {
              "class": 3,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([23.001141567762556, 39.57583699957153]),
            {
              "class": 3,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.990155239637556, 39.647778165980114]),
            {
              "class": 3,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([23.020367641981306, 39.63561689791066]),
            {
              "class": 3,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([23.031353970106306, 39.609171981237054]),
            {
              "class": 3,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([23.04371358924693, 39.57530774355931]),
            {
              "class": 3,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([23.070492764051618, 39.53983838626005]),
            {
              "class": 3,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([23.08216573768443, 39.587479609460395]),
            {
              "class": 3,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([23.084225674207868, 39.61128794644237]),
            {
              "class": 3,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([23.036160488660993, 39.657294188315184]),
            {
              "class": 3,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([23.078045864637556, 39.656236917188494]),
            {
              "class": 3,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([23.047146816785993, 39.63773205467431]),
            {
              "class": 3,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([23.071866055067243, 39.63508809861337]),
            {
              "class": 3,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([23.103451748426618, 39.63667448437762]),
            {
              "class": 3,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([23.106198330457868, 39.57530774355931]),
            {
              "class": 3,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.94483663612193, 39.61499072993869]),
            {
              "class": 3,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.974362392957868, 39.63826083375879]),
            {
              "class": 3,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([23.005948086317243, 39.63032872302613]),
            {
              "class": 3,
              "system:index": "24"
            })]),
    test_forest = 
    /* color: #00ff25 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.947239895399274, 39.54222122469269]),
            {
              "class": 0,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([23.024144192274274, 39.481300799153736]),
            {
              "class": 0,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.997365017469587, 39.47123054395815]),
            {
              "class": 0,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([23.067402859266462, 39.49931761720097]),
            {
              "class": 0,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([23.01178457313365, 39.481830772202464]),
            {
              "class": 0,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.930760403211774, 39.52951180772029]),
            {
              "class": 0,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.856602688368024, 39.574513851964284]),
            {
              "class": 0,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.877888699110212, 39.56233970901497]),
            {
              "class": 0,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.9486131864149, 39.5300414132184]),
            {
              "class": 0,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([23.035817165907087, 39.47865087333517]),
            {
              "class": 0,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.839436550672712, 39.640640289611504]),
            {
              "class": 0,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.96783926063365, 39.475470829089886]),
            {
              "class": 0,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.980198879774274, 39.49030979175465]),
            {
              "class": 0,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.857543948220847, 39.646079376940556]),
            {
              "class": 0,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.868530276345847, 39.64449320689613]),
            {
              "class": 0,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.793685915994285, 39.60694322965976]),
            {
              "class": 0,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.838317874002097, 39.65876742739241]),
            {
              "class": 0,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.892562869119285, 39.59900752876785]),
            {
              "class": 0,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([23.047058108377097, 39.51377375501294]),
            {
              "class": 0,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([23.054611208963035, 39.47509288279094]),
            {
              "class": 0,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.933761599588035, 39.47827294431363]),
            {
              "class": 0,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.939254763650535, 39.52754530581437]),
            {
              "class": 0,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.971527102517722, 39.52754530581437]),
            {
              "class": 0,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.89393616013491, 39.58577933986238]),
            {
              "class": 0,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.807418826150535, 39.60271096901711]),
            {
              "class": 0,
              "system:index": "24"
            }),
        ee.Feature(
            ee.Geometry.Point([23.060791018533347, 39.46290130024887]),
            {
              "class": 0,
              "system:index": "25"
            }),
        ee.Feature(
            ee.Geometry.Point([23.034698489236472, 39.499999473685385]),
            {
              "class": 0,
              "system:index": "26"
            }),
        ee.Feature(
            ee.Geometry.Point([22.930328372048972, 39.55772722650758]),
            {
              "class": 0,
              "system:index": "27"
            }),
        ee.Feature(
            ee.Geometry.Point([22.744247439431785, 39.62651407024796]),
            {
              "class": 0,
              "system:index": "28"
            }),
        ee.Feature(
            ee.Geometry.Point([22.88256172680829, 39.645913675014384]),
            {
              "class": 0,
              "system:index": "29"
            }),
        ee.Feature(
            ee.Geometry.Point([22.87260536694501, 39.63956876132449]),
            {
              "class": 0,
              "system:index": "30"
            }),
        ee.Feature(
            ee.Geometry.Point([22.84960274243329, 39.637453660728845]),
            {
              "class": 0,
              "system:index": "31"
            }),
        ee.Feature(
            ee.Geometry.Point([22.86985878491376, 39.61656356940641]),
            {
              "class": 0,
              "system:index": "32"
            }),
        ee.Feature(
            ee.Geometry.Point([22.833809895753603, 39.62899261154203]),
            {
              "class": 0,
              "system:index": "33"
            }),
        ee.Feature(
            ee.Geometry.Point([22.818360371827822, 39.63005029928457]),
            {
              "class": 0,
              "system:index": "34"
            }),
        ee.Feature(
            ee.Geometry.Point([22.808747334718447, 39.61365432229309]),
            {
              "class": 0,
              "system:index": "35"
            }),
        ee.Feature(
            ee.Geometry.Point([22.827286763429385, 39.595667171516574]),
            {
              "class": 0,
              "system:index": "36"
            }),
        ee.Feature(
            ee.Geometry.Point([22.811837239503603, 39.57926305049189]),
            {
              "class": 0,
              "system:index": "37"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82969002270673, 39.58323214558049]),
            {
              "class": 0,
              "system:index": "38"
            }),
        ee.Feature(
            ee.Geometry.Point([22.810120625734072, 39.63190121392598]),
            {
              "class": 0,
              "system:index": "39"
            }),
        ee.Feature(
            ee.Geometry.Point([22.77544502758954, 39.64274129093849]),
            {
              "class": 0,
              "system:index": "40"
            }),
        ee.Feature(
            ee.Geometry.Point([22.765831990480166, 39.63428088855818]),
            {
              "class": 0,
              "system:index": "41"
            }),
        ee.Feature(
            ee.Geometry.Point([22.762398762941103, 39.62952145743449]),
            {
              "class": 0,
              "system:index": "42"
            }),
        ee.Feature(
            ee.Geometry.Point([22.863678975343447, 39.6620377103408]),
            {
              "class": 0,
              "system:index": "43"
            }),
        ee.Feature(
            ee.Geometry.Point([22.878441853761416, 39.65913037537415]),
            {
              "class": 0,
              "system:index": "44"
            }),
        ee.Feature(
            ee.Geometry.Point([22.86058907055829, 39.63586729283496]),
            {
              "class": 0,
              "system:index": "45"
            }),
        ee.Feature(
            ee.Geometry.Point([22.94298653149579, 39.558090704531374]),
            {
              "class": 0,
              "system:index": "46"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82145027661298, 39.57820458674499]),
            {
              "class": 0,
              "system:index": "47"
            }),
        ee.Feature(
            ee.Geometry.Point([22.796387715577822, 39.60069346340625]),
            {
              "class": 0,
              "system:index": "48"
            }),
        ee.Feature(
            ee.Geometry.Point([22.79570107007001, 39.62264614553278]),
            {
              "class": 0,
              "system:index": "49"
            })]),
    test_rural = 
    /* color: #00ff31 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.664341946180524, 39.53798501091972]),
            {
              "class": 1,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.697300930555524, 39.53639636409612]),
            {
              "class": 1,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.699360867078962, 39.51203256011487]),
            {
              "class": 1,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.763390560682478, 39.51812431243998]),
            {
              "class": 1,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.653355618055524, 39.51256229891442]),
            {
              "class": 1,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.616963406141462, 39.51997821798501]),
            {
              "class": 1,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.579884548719587, 39.539044088602665]),
            {
              "class": 1,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.64374258094615, 39.58774419149918]),
            {
              "class": 1,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.684254665907087, 39.57557237207055]),
            {
              "class": 1,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.661595364149274, 39.59673937967079]),
            {
              "class": 1,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.66022207313365, 39.585098325647486]),
            {
              "class": 1,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.678074856336774, 39.593035620107145]),
            {
              "class": 1,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.67670156532115, 39.569750311463714]),
            {
              "class": 1,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.715840359266462, 39.53427811177335]),
            {
              "class": 1,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.728199978407087, 39.53533724601439]),
            {
              "class": 1,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.628890994119285, 39.58048735707848]),
            {
              "class": 1,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.50941467575991, 39.59530389048252]),
            {
              "class": 1,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.510787966775535, 39.58683768792527]),
            {
              "class": 1,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.503234866189597, 39.58472097563471]),
            {
              "class": 1,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.51216125779116, 39.58313339898449]),
            {
              "class": 1,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.541687014627097, 39.58154578596415]),
            {
              "class": 1,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.549926760720847, 39.60271096901711]),
            {
              "class": 1,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.56983948044741, 39.67251018732719]),
            {
              "class": 1,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.604171755838035, 39.66828193693057]),
            {
              "class": 1,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.577392581033347, 39.662467670100874]),
            {
              "class": 1,
              "system:index": "24"
            }),
        ee.Feature(
            ee.Geometry.Point([22.541687014627097, 39.666696276315285]),
            {
              "class": 1,
              "system:index": "25"
            }),
        ee.Feature(
            ee.Geometry.Point([22.56434631638491, 39.66141047811449]),
            {
              "class": 1,
              "system:index": "26"
            }),
        ee.Feature(
            ee.Geometry.Point([22.47645569138491, 39.64290700046675]),
            {
              "class": 1,
              "system:index": "27"
            }),
        ee.Feature(
            ee.Geometry.Point([22.499801638650535, 39.64026324223008]),
            {
              "class": 1,
              "system:index": "28"
            }),
        ee.Feature(
            ee.Geometry.Point([22.576019290017722, 39.64660809220308]),
            {
              "class": 1,
              "system:index": "29"
            }),
        ee.Feature(
            ee.Geometry.Point([22.748246059555797, 39.550051991982315]),
            {
              "class": 1,
              "system:index": "30"
            }),
        ee.Feature(
            ee.Geometry.Point([22.760262355942515, 39.54383066606397]),
            {
              "class": 1,
              "system:index": "31"
            }),
        ee.Feature(
            ee.Geometry.Point([22.70447240843275, 39.51708585155561]),
            {
              "class": 1,
              "system:index": "32"
            }),
        ee.Feature(
            ee.Geometry.Point([22.72421346678236, 39.568977276506516]),
            {
              "class": 1,
              "system:index": "33"
            }),
        ee.Feature(
            ee.Geometry.Point([22.68696294798353, 39.567124679486945]),
            {
              "class": 1,
              "system:index": "34"
            }),
        ee.Feature(
            ee.Geometry.Point([22.74240957273939, 39.55349333689835]),
            {
              "class": 1,
              "system:index": "35"
            }),
        ee.Feature(
            ee.Geometry.Point([22.750820980210094, 39.539594550527916]),
            {
              "class": 1,
              "system:index": "36"
            }),
        ee.Feature(
            ee.Geometry.Point([22.723355159897594, 39.52145575795467]),
            {
              "class": 1,
              "system:index": "37"
            }),
        ee.Feature(
            ee.Geometry.Point([22.739491329331187, 39.52026399256632]),
            {
              "class": 1,
              "system:index": "38"
            }),
        ee.Feature(
            ee.Geometry.Point([22.698120937485484, 39.50569631882892]),
            {
              "class": 1,
              "system:index": "39"
            }),
        ee.Feature(
            ee.Geometry.Point([22.694344387192515, 39.549654902738325]),
            {
              "class": 1,
              "system:index": "40"
            }),
        ee.Feature(
            ee.Geometry.Point([22.67803655638197, 39.55640511080451]),
            {
              "class": 1,
              "system:index": "41"
            }),
        ee.Feature(
            ee.Geometry.Point([22.666191921372203, 39.56249297038364]),
            {
              "class": 1,
              "system:index": "42"
            }),
        ee.Feature(
            ee.Geometry.Point([22.628941402573375, 39.562360631292115]),
            {
              "class": 1,
              "system:index": "43"
            }),
        ee.Feature(
            ee.Geometry.Point([22.66052709593275, 39.55931676248855]),
            {
              "class": 1,
              "system:index": "44"
            }),
        ee.Feature(
            ee.Geometry.Point([22.687649593491344, 39.53866786578836]),
            {
              "class": 1,
              "system:index": "45"
            }),
        ee.Feature(
            ee.Geometry.Point([22.68747793211439, 39.561169568104646]),
            {
              "class": 1,
              "system:index": "46"
            }),
        ee.Feature(
            ee.Geometry.Point([22.69348608030775, 39.558125647027055]),
            {
              "class": 1,
              "system:index": "47"
            }),
        ee.Feature(
            ee.Geometry.Point([22.651944027085094, 39.53641729419781]),
            {
              "class": 1,
              "system:index": "48"
            }),
        ee.Feature(
            ee.Geometry.Point([22.63632284178236, 39.567653997971995]),
            {
              "class": 1,
              "system:index": "49"
            })]),
    test_urban = 
    /* color: #ff0202 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.427797510421982, 39.6400088582002]),
            {
              "class": 2,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.418527796066513, 39.63657180875677]),
            {
              "class": 2,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.406511499679794, 39.631019291166766]),
            {
              "class": 2,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.418527796066513, 39.63392780834572]),
            {
              "class": 2,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.437753870285263, 39.63313458851518]),
            {
              "class": 2,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.4233343146212, 39.63313458851518]),
            {
              "class": 2,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.408228113449326, 39.6267885024351]),
            {
              "class": 2,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.412691309250107, 39.63049045672359]),
            {
              "class": 2,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.39689846257042, 39.626259635653135]),
            {
              "class": 2,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.40067501286339, 39.62176410480081]),
            {
              "class": 2,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.432260706222763, 39.63868693631962]),
            {
              "class": 2,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.4288274786837, 39.63789377106342]),
            {
              "class": 2,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.433977319992294, 39.64979029481682]),
            {
              "class": 2,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.44462032536339, 39.62943277571008]),
            {
              "class": 2,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.450456812179794, 39.62890392913975]),
            {
              "class": 2,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.409851077127097, 39.61540697491882]),
            {
              "class": 2,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.42976379685366, 39.621225199551986]),
            {
              "class": 2,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.431823733377097, 39.6058851887494]),
            {
              "class": 2,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.540353617577082, 39.56610593649532]),
            {
              "class": 2,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.467912516502864, 39.5618711809383]),
            {
              "class": 2,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.462419352440364, 39.5618711809383]),
            {
              "class": 2,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.465852579979426, 39.567429244573525]),
            {
              "class": 2,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.465165934471614, 39.56028308093497]),
            {
              "class": 2,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.46928580751849, 39.55922432739685]),
            {
              "class": 2,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.541726908592707, 39.56584127184916]),
            {
              "class": 2,
              "system:index": "24"
            }),
        ee.Feature(
            ee.Geometry.Point([22.53417380800677, 39.56610593649532]),
            {
              "class": 2,
              "system:index": "25"
            }),
        ee.Feature(
            ee.Geometry.Point([22.53863700380755, 39.56478260316297]),
            {
              "class": 2,
              "system:index": "26"
            }),
        ee.Feature(
            ee.Geometry.Point([22.69999869814349, 39.49063563786655]),
            {
              "class": 2,
              "system:index": "27"
            }),
        ee.Feature(
            ee.Geometry.Point([22.698625407127864, 39.487191177003666]),
            {
              "class": 2,
              "system:index": "28"
            }),
        ee.Feature(
            ee.Geometry.Point([22.6951921795888, 39.49037068539648]),
            {
              "class": 2,
              "system:index": "29"
            }),
        ee.Feature(
            ee.Geometry.Point([22.74213062300184, 39.46231458054655]),
            {
              "class": 2,
              "system:index": "30"
            }),
        ee.Feature(
            ee.Geometry.Point([22.740371093888072, 39.4626624707378]),
            {
              "class": 2,
              "system:index": "31"
            }),
        ee.Feature(
            ee.Geometry.Point([22.744051084656505, 39.462910962666925]),
            {
              "class": 2,
              "system:index": "32"
            }),
        ee.Feature(
            ee.Geometry.Point([22.746518716950206, 39.46290267961692]),
            {
              "class": 2,
              "system:index": "33"
            }),
        ee.Feature(
            ee.Geometry.Point([22.74693714155653, 39.46185072425314]),
            {
              "class": 2,
              "system:index": "34"
            }),
        ee.Feature(
            ee.Geometry.Point([22.73988829626539, 39.46349905669787]),
            {
              "class": 2,
              "system:index": "35"
            }),
        ee.Feature(
            ee.Geometry.Point([22.743568287033824, 39.462157201079215]),
            {
              "class": 2,
              "system:index": "36"
            }),
        ee.Feature(
            ee.Geometry.Point([22.739748821396617, 39.46250509205716]),
            {
              "class": 2,
              "system:index": "37"
            }),
        ee.Feature(
            ee.Geometry.Point([22.427564871563686, 39.61382156869078]),
            {
              "class": 2,
              "system:index": "38"
            }),
        ee.Feature(
            ee.Geometry.Point([22.43074060703732, 39.61408605011458]),
            {
              "class": 2,
              "system:index": "39"
            }),
        ee.Feature(
            ee.Geometry.Point([22.434002173199428, 39.611441190405]),
            {
              "class": 2,
              "system:index": "40"
            }),
        ee.Feature(
            ee.Geometry.Point([22.433744681133998, 39.60800272171731]),
            {
              "class": 2,
              "system:index": "41"
            }),
        ee.Feature(
            ee.Geometry.Point([22.439495337261928, 39.60780434331365]),
            {
              "class": 2,
              "system:index": "42"
            }),
        ee.Feature(
            ee.Geometry.Point([22.44146944309689, 39.606151167846164]),
            {
              "class": 2,
              "system:index": "43"
            }),
        ee.Feature(
            ee.Geometry.Point([22.43245722080685, 39.60264630531993]),
            {
              "class": 2,
              "system:index": "44"
            }),
        ee.Feature(
            ee.Geometry.Point([22.429023993267787, 39.60588665610853]),
            {
              "class": 2,
              "system:index": "45"
            }),
        ee.Feature(
            ee.Geometry.Point([22.429882300152553, 39.62539921291682]),
            {
              "class": 2,
              "system:index": "46"
            }),
        ee.Feature(
            ee.Geometry.Point([22.433058035626186, 39.62592808627515]),
            {
              "class": 2,
              "system:index": "47"
            }),
        ee.Feature(
            ee.Geometry.Point([22.426792395367396, 39.62645695559122]),
            {
              "class": 2,
              "system:index": "48"
            }),
        ee.Feature(
            ee.Geometry.Point([22.43194223667599, 39.62447367481305]),
            {
              "class": 2,
              "system:index": "49"
            })]),
    test_sea = 
    /* color: #1129ff */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.938760797619256, 39.661684771845735]),
            {
              "class": 3,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.95592693531457, 39.64899725690735]),
            {
              "class": 3,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.953523676037225, 39.63630741326352]),
            {
              "class": 3,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.961763422130975, 39.610656247123835]),
            {
              "class": 3,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.994722406505975, 39.648468559914086]),
            {
              "class": 3,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([23.037637750744256, 39.66802765598954]),
            {
              "class": 3,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.99334911549035, 39.57652811131839]),
            {
              "class": 3,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([23.071626703380975, 39.612507680522334]),
            {
              "class": 3,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([23.08226970875207, 39.64476756776148]),
            {
              "class": 3,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([23.033861200451287, 39.60192739420471]),
            {
              "class": 3,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([23.03077129566613, 39.581026579415095]),
            {
              "class": 3,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([23.00330547535363, 39.61700381263697]),
            {
              "class": 3,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([23.03557781422082, 39.64371010504697]),
            {
              "class": 3,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([23.007768671154412, 39.66379913125321]),
            {
              "class": 3,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.929834406017694, 39.65507698174346]),
            {
              "class": 3,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([23.074563822655207, 39.524806039926375]),
            {
              "class": 3,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([23.012765726952082, 39.5968001799967]),
            {
              "class": 3,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.984269938377864, 39.62166312920147]),
            {
              "class": 3,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([23.076623759178645, 39.56610593649532]),
            {
              "class": 3,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([23.048127970604426, 39.54466482737876]),
            {
              "class": 3,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.95817740908099, 39.57960249392911]),
            {
              "class": 3,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.94890769472552, 39.60632321545324]),
            {
              "class": 3,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.993539652733332, 39.60076827057545]),
            {
              "class": 3,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([23.09825309267474, 39.55922432739685]),
            {
              "class": 3,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([23.100313029198176, 39.51871487359834]),
            {
              "class": 3,
              "system:index": "24"
            }),
        ee.Feature(
            ee.Geometry.Point([23.085893473534114, 39.53857540318378]),
            {
              "class": 3,
              "system:index": "25"
            }),
        ee.Feature(
            ee.Geometry.Point([23.002466044334895, 39.57351613645347]),
            {
              "class": 3,
              "system:index": "26"
            }),
        ee.Feature(
            ee.Geometry.Point([23.025125346092707, 39.549165362725816]),
            {
              "class": 3,
              "system:index": "27"
            }),
        ee.Feature(
            ee.Geometry.Point([22.98907645693255, 39.56769390315865]),
            {
              "class": 3,
              "system:index": "28"
            }),
        ee.Feature(
            ee.Geometry.Point([22.927278361229426, 39.61399359723786]),
            {
              "class": 3,
              "system:index": "29"
            }),
        ee.Feature(
            ee.Geometry.Point([23.113266241802943, 39.540009307551664]),
            {
              "class": 3,
              "system:index": "30"
            }),
        ee.Feature(
            ee.Geometry.Point([23.059021246685756, 39.55483449208983]),
            {
              "class": 3,
              "system:index": "31"
            }),
        ee.Feature(
            ee.Geometry.Point([23.11807276035763, 39.48703636641997]),
            {
              "class": 3,
              "system:index": "32"
            }),
        ee.Feature(
            ee.Geometry.Point([22.971130621685756, 39.60458158524667]),
            {
              "class": 3,
              "system:index": "33"
            }),
        ee.Feature(
            ee.Geometry.Point([23.111206305279506, 39.51352788602693]),
            {
              "class": 3,
              "system:index": "34"
            }),
        ee.Feature(
            ee.Geometry.Point([23.09610010410763, 39.60246541508802]),
            {
              "class": 3,
              "system:index": "35"
            }),
        ee.Feature(
            ee.Geometry.Point([23.080307257427943, 39.6029944636902]),
            {
              "class": 3,
              "system:index": "36"
            }),
        ee.Feature(
            ee.Geometry.Point([23.063827765240443, 39.57600783217922]),
            {
              "class": 3,
              "system:index": "37"
            }),
        ee.Feature(
            ee.Geometry.Point([23.118759405865443, 39.59241272375064]),
            {
              "class": 3,
              "system:index": "38"
            }),
        ee.Feature(
            ee.Geometry.Point([23.006149542584193, 39.55906967730295]),
            {
              "class": 3,
              "system:index": "39"
            }),
        ee.Feature(
            ee.Geometry.Point([22.94160486484982, 39.60087824503173]),
            {
              "class": 3,
              "system:index": "40"
            }),
        ee.Feature(
            ee.Geometry.Point([22.923752081646693, 39.64742011614559]),
            {
              "class": 3,
              "system:index": "41"
            }),
        ee.Feature(
            ee.Geometry.Point([22.902466070904506, 39.66380809147524]),
            {
              "class": 3,
              "system:index": "42"
            }),
        ee.Feature(
            ee.Geometry.Point([23.02468897129513, 39.64266158912485]),
            {
              "class": 3,
              "system:index": "43"
            }),
        ee.Feature(
            ee.Geometry.Point([23.053528082623256, 39.615690417611546]),
            {
              "class": 3,
              "system:index": "44"
            }),
        ee.Feature(
            ee.Geometry.Point([23.08992029453732, 39.645833976857155]),
            {
              "class": 3,
              "system:index": "45"
            }),
        ee.Feature(
            ee.Geometry.Point([23.058334601177943, 39.6569361877644]),
            {
              "class": 3,
              "system:index": "46"
            }),
        ee.Feature(
            ee.Geometry.Point([23.10433985020138, 39.62521085518718]),
            {
              "class": 3,
              "system:index": "47"
            }),
        ee.Feature(
            ee.Geometry.Point([23.124252569927943, 39.64213284368652]),
            {
              "class": 3,
              "system:index": "48"
            }),
        ee.Feature(
            ee.Geometry.Point([23.119446051373256, 39.66169373234193]),
            {
              "class": 3,
              "system:index": "49"
            })]),
    lake = 
    /* color: #2fcad6 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.81558125209444, 39.461108372628615]),
            {
              "class": 4,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.825880934711627, 39.47913042125348]),
            {
              "class": 4,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.845107008930377, 39.47807042996582]),
            {
              "class": 4,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82656758021944, 39.47383030328586]),
            {
              "class": 4,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.805968214985064, 39.49820750212831]),
            {
              "class": 4,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.794295241352252, 39.51304161295528]),
            {
              "class": 4,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.798415114399127, 39.49661794530066]),
            {
              "class": 4,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.84304707240694, 39.50244614262649]),
            {
              "class": 4,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.830000807758502, 39.50138650673526]),
            {
              "class": 4,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.832747389789752, 39.49555822055503]),
            {
              "class": 4,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.842360426899127, 39.47860042762878]),
            {
              "class": 4,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.812148024555377, 39.47648041274739]),
            {
              "class": 4,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.810774733539752, 39.49237894938881]),
            {
              "class": 4,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.820387770649127, 39.49926718648604]),
            {
              "class": 4,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.838927199360064, 39.47489035918501]),
            {
              "class": 4,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.812148024555377, 39.461108372628615]),
            {
              "class": 4,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.710176866587673, 39.561861540874375]),
            {
              "class": 4,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.708460252818142, 39.55656773204374]),
            {
              "class": 4,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.71498338514236, 39.55683243208136]),
            {
              "class": 4,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.707430284556423, 39.56702261545526]),
            {
              "class": 4,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.70554200940994, 39.560405783724555]),
            {
              "class": 4,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.714811723765408, 39.54955281299689]),
            {
              "class": 4,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.62709276014236, 39.63606463082708]),
            {
              "class": 4,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.628809373911892, 39.63355281441973]),
            {
              "class": 4,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.636534135874783, 39.63408162545359]),
            {
              "class": 4,
              "system:index": "24"
            })]),
    test_lake = 
    /* color: #2fcad6 */
    /* shown: false */
    ee.FeatureCollection(
        [ee.Feature(
            ee.Geometry.Point([22.81185019743873, 39.454255949371806]),
            {
              "class": 4,
              "system:index": "0"
            }),
        ee.Feature(
            ee.Geometry.Point([22.807730324391855, 39.46538886189558]),
            {
              "class": 4,
              "system:index": "1"
            }),
        ee.Feature(
            ee.Geometry.Point([22.815283424977792, 39.47121967683944]),
            {
              "class": 4,
              "system:index": "2"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82832968962623, 39.471749726697105]),
            {
              "class": 4,
              "system:index": "3"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82357603418287, 39.46795897836946]),
            {
              "class": 4,
              "system:index": "4"
            }),
        ee.Feature(
            ee.Geometry.Point([22.817653716677988, 39.46590490077603]),
            {
              "class": 4,
              "system:index": "5"
            }),
        ee.Feature(
            ee.Geometry.Point([22.81336218225416, 39.46259174463739]),
            {
              "class": 4,
              "system:index": "6"
            }),
        ee.Feature(
            ee.Geometry.Point([22.804264129275644, 39.47021176794717]),
            {
              "class": 4,
              "system:index": "7"
            }),
        ee.Feature(
            ee.Geometry.Point([22.813705505008066, 39.476638443220985]),
            {
              "class": 4,
              "system:index": "8"
            }),
        ee.Feature(
            ee.Geometry.Point([22.834976712580485, 39.479340740682915]),
            {
              "class": 4,
              "system:index": "9"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82364706170158, 39.484242975445554]),
            {
              "class": 4,
              "system:index": "10"
            }),
        ee.Feature(
            ee.Geometry.Point([22.84132818352775, 39.48371302077817]),
            {
              "class": 4,
              "system:index": "11"
            }),
        ee.Feature(
            ee.Geometry.Point([22.839954892512125, 39.47801575305576]),
            {
              "class": 4,
              "system:index": "12"
            }),
        ee.Feature(
            ee.Geometry.Point([22.854116956110758, 39.484110487157324]),
            {
              "class": 4,
              "system:index": "13"
            }),
        ee.Feature(
            ee.Geometry.Point([22.8290543950756, 39.48583281521702]),
            {
              "class": 4,
              "system:index": "14"
            }),
        ee.Feature(
            ee.Geometry.Point([22.81532148491935, 39.48464043879585]),
            {
              "class": 4,
              "system:index": "15"
            }),
        ee.Feature(
            ee.Geometry.Point([22.809426731608713, 39.49568340823205]),
            {
              "class": 4,
              "system:index": "16"
            }),
        ee.Feature(
            ee.Geometry.Point([22.79432053043684, 39.50124677289578]),
            {
              "class": 4,
              "system:index": "17"
            }),
        ee.Feature(
            ee.Geometry.Point([22.818353123210276, 39.50012088979603]),
            {
              "class": 4,
              "system:index": "18"
            }),
        ee.Feature(
            ee.Geometry.Point([22.828051991008127, 39.50276999747173]),
            {
              "class": 4,
              "system:index": "19"
            }),
        ee.Feature(
            ee.Geometry.Point([22.832686848185862, 39.49760414397905]),
            {
              "class": 4,
              "system:index": "20"
            }),
        ee.Feature(
            ee.Geometry.Point([22.807195133708323, 39.50290245020498]),
            {
              "class": 4,
              "system:index": "21"
            }),
        ee.Feature(
            ee.Geometry.Point([22.805564350627268, 39.510159584673254]),
            {
              "class": 4,
              "system:index": "22"
            }),
        ee.Feature(
            ee.Geometry.Point([22.79723877384504, 39.512808309683834]),
            {
              "class": 4,
              "system:index": "23"
            }),
        ee.Feature(
            ee.Geometry.Point([22.80479187443098, 39.51724469784813]),
            {
              "class": 4,
              "system:index": "24"
            }),
        ee.Feature(
            ee.Geometry.Point([22.80050034000715, 39.50280884386792]),
            {
              "class": 4,
              "system:index": "25"
            }),
        ee.Feature(
            ee.Geometry.Point([22.790887302897776, 39.50539162518955]),
            {
              "class": 4,
              "system:index": "26"
            }),
        ee.Feature(
            ee.Geometry.Point([22.791659779094065, 39.49704690887099]),
            {
              "class": 4,
              "system:index": "27"
            }),
        ee.Feature(
            ee.Geometry.Point([22.798869556926096, 39.49645081936785]),
            {
              "class": 4,
              "system:index": "28"
            }),
        ee.Feature(
            ee.Geometry.Point([22.801701969645823, 39.49777545576653]),
            {
              "class": 4,
              "system:index": "29"
            }),
        ee.Feature(
            ee.Geometry.Point([22.80951256229719, 39.50029219538076]),
            {
              "class": 4,
              "system:index": "30"
            }),
        ee.Feature(
            ee.Geometry.Point([22.819125599406565, 39.50340487884645]),
            {
              "class": 4,
              "system:index": "31"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82848114445051, 39.50923250706329]),
            {
              "class": 4,
              "system:index": "32"
            }),
        ee.Feature(
            ee.Geometry.Point([22.83294434025129, 39.505192953111155]),
            {
              "class": 4,
              "system:index": "33"
            }),
        ee.Feature(
            ee.Geometry.Point([22.838094181559885, 39.502279030706745]),
            {
              "class": 4,
              "system:index": "34"
            }),
        ee.Feature(
            ee.Geometry.Point([22.84547562076887, 39.497510530506204]),
            {
              "class": 4,
              "system:index": "35"
            }),
        ee.Feature(
            ee.Geometry.Point([22.855775303386057, 39.49552355886958]),
            {
              "class": 4,
              "system:index": "36"
            }),
        ee.Feature(
            ee.Geometry.Point([22.842042393229807, 39.489628542176426]),
            {
              "class": 4,
              "system:index": "37"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82178635074934, 39.49241052245013]),
            {
              "class": 4,
              "system:index": "38"
            }),
        ee.Feature(
            ee.Geometry.Point([22.812173313639963, 39.49247675871896]),
            {
              "class": 4,
              "system:index": "39"
            }),
        ee.Feature(
            ee.Geometry.Point([22.81251663639387, 39.48876743048474]),
            {
              "class": 4,
              "system:index": "40"
            }),
        ee.Feature(
            ee.Geometry.Point([22.830369419596995, 39.49241052245013]),
            {
              "class": 4,
              "system:index": "41"
            }),
        ee.Feature(
            ee.Geometry.Point([22.84144157841047, 39.50115316432874]),
            {
              "class": 4,
              "system:index": "42"
            }),
        ee.Feature(
            ee.Geometry.Point([22.845132298014963, 39.50777564582704]),
            {
              "class": 4,
              "system:index": "43"
            }),
        ee.Feature(
            ee.Geometry.Point([22.83920998051008, 39.510159584673254]),
            {
              "class": 4,
              "system:index": "44"
            }),
        ee.Feature(
            ee.Geometry.Point([22.82496208622297, 39.507312092664336]),
            {
              "class": 4,
              "system:index": "45"
            }),
        ee.Feature(
            ee.Geometry.Point([22.813374943278635, 39.508504080263386]),
            {
              "class": 4,
              "system:index": "46"
            }),
        ee.Feature(
            ee.Geometry.Point([22.803676075480784, 39.50678231383458]),
            {
              "class": 4,
              "system:index": "47"
            }),
        ee.Feature(
            ee.Geometry.Point([22.79552216007551, 39.50472938271943]),
            {
              "class": 4,
              "system:index": "48"
            }),
        ee.Feature(
            ee.Geometry.Point([22.710114381558, 39.56028263717182]),
            {
              "class": 4,
              "system:index": "49"
            })]);


/* End of Imports */





//Filtering data

var l8 = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
filterBounds(ROI);

// Adding Indices

var calculate_indices = function(image){
  
  // EVI = 2.5*(NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
  var nir = image.select('B5');
  var red = image.select('B4');
  var blue = image.select('B2');
  var evi = (nir.multiply(2.5).subtract(red.multiply(2.5)).divide(nir.add(red.multiply(6)).
    add(blue.multiply(-7.5)).add(1))).rename('EVI');
  
  var ndvi = image.normalizedDifference(['B5', 'B4']).float().rename('NDVI');
  var ndwi = image.normalizedDifference(['B5', 'B6']).rename('NDWI');
  
  return image.addBands(ndvi).addBands(ndwi).addBands(evi);
};

var l8 = l8.map(calculate_indices);

// Step 2 - Indices of image with less cloud cover


// RGB on ROI - 2019

var RGB_viz = {min: '8000', max: '10500',
bands: ['B4', 'B3', 'B2']};  // RGB visualization

var RGB_clearest_viz = {min: '6500', max: '9000',
bands: ['B4', 'B3', 'B2']};  // RGB clearest visualization

Map.addLayer(l8.filterDate('2019-01-01',
'2019-12-31').sort('CLOUD_COVER').median(), RGB_viz, 'RGB 2019');

Map.addLayer(l8.filterDate('2019-01-01',
'2019-12-31').sort('CLOUD_COVER').first().clip(ROI), RGB_clearest_viz, 'Clearest RGB 2019');


// False Color on ROI - 2019

var False_viz = {min: '6500', max: '15000',
bands: ['B5', 'B4', 'B3']}; // Pseudo visualization

Map.addLayer(l8.filterDate('2019-01-01',
'2019-12-31').sort('CLOUD_COVER').first().clip(ROI), False_viz, 'Clearest False color 2019');


// NDVI clearest on ROI - 2019

var NDVI_viz = {min: '-0.1', max: '0.35', bands: 'NDVI',
palette: 'orangered, yellow, green'}; // NDVI visualization

Map.addLayer(l8.filterDate('2019-01-01',
'2019-12-31').sort('CLOUD_COVER').first().clip(ROI), NDVI_viz, 'Clearest NDVI 2019');


// Step 3

var NDVI_greenest_viz = {min: '-0.15', max: '0.55', bands: 'NDVI',
palette: 'orangered, yellow, green'};


var Season_viz = {min: '0', max: '366', bands: 'doy',
  palette: 'lightblue, green, yellow, orangered'
};


//DOY for max ndvi
var addDOY = function(image){
  var img_date = ee.Date(image.date());
  var img_doy = ee.Number.parse(img_date.format('D'));
  return image.addBands(ee.Image(img_doy).rename('doy').toInt());
};

var greenest_pixels2019 = l8.filterDate('2019-01-01', '2019-12-31')
.map(addDOY).qualityMosaic('NDVI').select('NDVI', 'doy');

// Quality Mosaic for 2019

Map.addLayer(greenest_pixels2019.clip(ROI), NDVI_greenest_viz,
'Greenest pixels for year 2019');

// Seasonality Mapping for 2019

Map.addLayer(greenest_pixels2019.clip(ROI), Season_viz,
'Seasonality Mapping 2019');

var greenest_pixels2018 = l8.filterDate('2018-01-01', '2018-12-31')
.map(addDOY).qualityMosaic('NDVI').select('NDVI', 'doy');

// Quality Mosaic for 2018

Map.addLayer(greenest_pixels2018.clip(ROI), NDVI_greenest_viz,
'Greenest pixels for year 2018');

// Seasonality Mapping for 2018

Map.addLayer(greenest_pixels2018.clip(ROI), Season_viz,
'Seasonality Mapping 2018');

// Step 4 NDVI - Harmonic curves

// This field contains UNIX time in milliseconds.
var timeField = 'system:time_start';

// Use this function to add variables for NDVI, time and a constant
// to Landsat 8 imagery.
var addVariables = function(image) {
  // Compute time in fractional years since the epoch.
  var date = ee.Date(image.get(timeField));
  var years = date.difference(ee.Date('1970-01-01'), 'year');
  // Return the image with the added bands.
  return image
    // Add a time band.
    .addBands(ee.Image(years).rename('t').float())
    // Add a constant band.
    .addBands(ee.Image.constant(1));
};

var all_data_ndvi = l8.map(addVariables);


var print_harmonic_model = function(data, poly, title){ // A function to generate harmonic plot
  // Harmonic trend ----------------------------------------------------------------
  // Use these independent variables in the harmonic regression.
  var harmonicIndependents = ee.List(['constant', 't', 'cos', 'sin']);
  // Add harmonic terms as new image bands.
  var harmonicLandsat = data.map(function(image) {
    var timeRadians = image.select('t').multiply(2 * Math.PI);
    return image
      .addBands(timeRadians.cos().rename('cos'))
      .addBands(timeRadians.sin().rename('sin'));
  });
  
  // The output of the regression reduction is a 4x1 array image.
  var harmonicTrend = harmonicLandsat
    .select(harmonicIndependents.add('NDVI'))
    .reduce(ee.Reducer.linearRegression(harmonicIndependents.length(), 1));

  // Turn the array image into a multi-band image of coefficients.
  var harmonicTrendCoefficients = harmonicTrend.select('coefficients')
    .arrayProject([0])
    .arrayFlatten([harmonicIndependents]);
    
  // Compute fitted values.
  var fittedHarmonic = harmonicLandsat.map(function(image) {
    return image.addBands(
      image.select(harmonicIndependents)
        .multiply(harmonicTrendCoefficients)
        .reduce('sum')
        .rename('fitted'));
    
  });
  
  // Plot the fitted model and the original data at the ROI.
  print(ui.Chart.image.series(
    fittedHarmonic.select(['fitted','NDVI']), poly, ee.Reducer.mean(), 30)
      .setSeriesNames(['NDVI', 'fitted'])
      .setOptions({
        title: 'Harmonic model' + title + ': original and fitted values',
        lineWidth: 1,
        pointSize: 3,
  }));
};

print_harmonic_model(all_data_ndvi, Rural1, ' on Rural1'); // ROI 1
print_harmonic_model(all_data_ndvi, Rural2, ' on Rural2'); // ROI 2
print_harmonic_model(all_data_ndvi, Rural3, ' on Rural3'); // ROI 3
print_harmonic_model(all_data_ndvi, Rural4, ' on Rural4'); // ROI 4


// Step 5 - Classification Part

var classification_img = L8.filter(ee.Filter.lt('CLOUD_COVER', 20)).
filterBounds(ROI).mean().clip(ROI);


Map.addLayer(classification_img, RGB_viz, 'Classification RGB');

var features = classification_img.bandNames();
var training_pts = forest.merge(rural).merge(urban).merge(sea).merge(lake);
var test_pts = test_forest.merge(test_rural).merge(test_urban).merge(test_sea).
merge(test_lake);

var training_data = classification_img.sampleRegions({collection: training_pts,
  properties: ['class'], scale: 30
});

var test_data = classification_img.sampleRegions({collection: test_pts,
  properties: ['class'], scale: 30
});

var CART = ee.Classifier.smileCart();
// Create an SVM classifier with custom parameters.
var SVM = ee.Classifier.libsvm({
  kernelType: 'LINEAR',
  cost: 1
});


var CART = CART.train({features: training_data,
  classProperty: 'class', inputProperties: features});
  
var SVM = SVM.train({features: training_data,
  classProperty: 'class', inputProperties: features});
  
var CART_img = classification_img.classify(CART);
var SVM_img = classification_img.classify(SVM);

var Class_viz = {min: 0, max: 4,
palette: ['green','lightgreen', 'red', 'blue', '#689EDF']};

Map.addLayer(CART_img, Class_viz, 'Classified Image - CART');
Map.addLayer(SVM_img, Class_viz, 'Classified Image - SVM');


var evaluation = function(classifier, test_data, features, title){
  
  var confusionMatrix = ee.ConfusionMatrix(test_data.classify(classifier).errorMatrix({
  actual: 'class',
  predicted: 'classification'}));
  
  print(title);
  print('Confusion Matrix', confusionMatrix);
  print('Overall accuracy', confusionMatrix.accuracy());
};


evaluation(CART, test_data, features, 'CART Evaluation');
evaluation(SVM, test_data, features, 'SVM Evaluation');
