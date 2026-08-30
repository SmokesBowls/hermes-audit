 ╭─mytruelove@mytruelove in repo: godot_engain_3d_avatar on  main (a242b19) [!?⇡4] via  v3.14.7 took 5m39s
[⚡] × coredumpctl info 1075756 --no-pager
           PID: 1075756 (godot)
           TID: 1075756 (godot)
           UID: 1000 (mytruelove)
           GID: 1000 (mytruelove)
        Signal: 11 (SEGV) si_code: SEGV_MAPERR
     Timestamp: Sun 2026-08-23 19:22:42 PDT (1min 31s ago)
  Command Line: godot --editor --path /mnt/data-drive/godot_engain_3d_avatar
    Executable: /home/mytruelove/applications/Godot_v4.6.1-stable_linux.x86_64
 Control Group: /user.slice/user-1000.slice/user@1000.service/app.slice/app-org.gnome.Terminal.slice/vte-spawn-34f42e68-7b17-419c-9cca-6edbde556ef7.scope
          Unit: user@1000.service
     User Unit: vte-spawn-34f42e68-7b17-419c-9cca-6edbde556ef7.scope
         Slice: user-1000.slice
     Owner UID: 1000 (mytruelove)
       Boot ID: ba399898262841988021e2cf8f9e5c0d
    Machine ID: b2d7a572607c4e2a80bdb981d21c5e3c
      Hostname: mytruelove
       Storage: /var/lib/systemd/coredump/core.godot.1000.ba399898262841988021e2cf8f9e5c0d.1075756.1787538162000000.zst (present)
  Size on Disk: 136.8M
       Message: Process 1075756 (godot) of user 1000 dumped core.
                
                Module Godot_v4.6.1-stable_linux.x86_64 without build-id.
                Stack trace of thread 1075756:
                #0  0x00007f96b8782f07 n/a (libgcc_s.so.1 + 0x20f07)
                #1  0x00007f96b8784f06 _Unwind_Backtrace (libgcc_s.so.1 + 0x22f06)
                #2  0x00007f96b8d2c268 __backtrace (libc.so.6 + 0x12c268)
                #3  0x00000000004f9683 n/a (Godot_v4.6.1-stable_linux.x86_64 + 0xf9683)
                #4  0x00007f96b8c3e6f0 n/a (libc.so.6 + 0x3e6f0)
                #5  0x0000000000000361 n/a (n/a + 0x0)
                ELF object binary architecture: AMD x86-64

 ╭─mytruelove@mytruelove in repo: godot_engain_3d_avatar on  main (a242b19) [!?⇡4] via  v3.14.7 took 0s
 ╰─λ cd /mnt/data-drive/godot_engain_3d_avatar

godot --editor --path "$PWD" --verbose 2>&1 | tee /tmp/godot-editor-crash.log
WorkerThreadPool: 8 threads, 6 max low-priority.
Godot Engine v4.6.1.stable.official.14d19694e - https://godotengine.org
TextServer: Added interface "Dummy"
TextServer: Added interface "ICU / HarfBuzz / Graphite (Built-in)"
Unrecognized output string "misc2" in mapping:
030000000d0f0000ab01000011010000,Horipad Steam,a:b0,b:b1,back:b10,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b12,leftshoulder:b6,leftstick:b13,lefttrigger:a5,leftx:a0,lefty:a1,misc2:b2,paddle1:b19,paddle2:b18,paddle3:b15,paddle4:b5,rightshoulder:b7,rightstick:b14,righttrigger:a4,rightx:a2,righty:a3,start:b11,x:b3,y:b4,platform:Linux,
Unrecognized output string "misc2" in mapping:
050000000d0f00009601000091000000,Horipad Steam,a:b0,b:b1,back:b10,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b12,leftshoulder:b6,leftstick:b13,lefttrigger:a5,leftx:a0,lefty:a1,misc2:b2,paddle1:b19,paddle2:b18,paddle3:b15,paddle4:b5,rightshoulder:b7,rightstick:b14,righttrigger:a4,rightx:a2,righty:a3,start:b11,x:b3,y:b4,platform:Linux,
Unrecognized output string "misc2" in mapping:
030000007e0500006920000011010000,Nintendo Switch 2 Pro Controller,a:b0,b:b1,back:b14,dpdown:b8,dpleft:b10,dpright:b9,dpup:b11,guide:b16,leftshoulder:b12,leftstick:b15,lefttrigger:b13,leftx:a0,lefty:a1~,misc1:b17,misc2:b20,paddle1:b18,paddle2:b19,rightshoulder:b4,rightstick:b7,righttrigger:b5,rightx:a2,righty:a3~,start:b6,x:b2,y:b3,platform:Linux,
SDL: Init OK!
Xshape 1.1 detected.
Xinerama 1.1 detected.
Xrandr 1.6 detected.
Xrender 0.11 detected.
Xinput 2.2 detected.
XInput: Refreshing devices.
XInput: No touch devices found.
Detecting GPUs, set DRI_PRIME in the environment to override GPU detection logic.
Only one GPU found, using default.
XcursorGetTheme could not get cursor theme
DBus 1.16.2 detected.
FreeDesktopScreenSaver: Acquired screensaver inhibition cookie: 1755907198
Using "default" pen tablet driver...
Shader 'CanvasSdfShaderGLES3' SHA256: 3b0ba7b5aa447455ee78b6016910c9be153c8af24ddf001ac577ab25bc8763da
Shader 'SkeletonShaderGLES3' SHA256: b9898151f9af4f78e3ba0f209025516181c47cb21bfe23086e29c8c13c24b7ff
Shader 'ParticlesShaderGLES3' SHA256: 10840b41ad3bbb5a7e9683749e3c4dee485561a870dc6f0f142527c9c1faa69a
Shader 'ParticlesCopyShaderGLES3' SHA256: afa1b0f07f968421b2930a23c730ede16ea0b220a00994ee98c2ad6ef9fa6307
Shader 'CopyShaderGLES3' SHA256: 2f5c0a88f17513d21c5a58b094b6f0bb2a109d426450b8dc9dbabda361936c77
Shader 'CubemapFilterShaderGLES3' SHA256: 93f329abbd19174cabf54d8997485740cb1760303e811f3e992e6331ae7b2024
Shader 'GlowShaderGLES3' SHA256: 0f477a49356fb3c03dae6f40da2b3d57ec4daad55c6e73ebc76304d5c8c42b1a
Shader 'PostShaderGLES3' SHA256: 51716a3e1e00f34a44c54de4a86d32ba444b7b296762f2ab60a1298e84641923
Shader 'FeedShaderGLES3' SHA256: 487b653ef51dbf691e2458ed838d361aa917082543e797e8f92eed2acfaff3f7
Shader 'CanvasShaderGLES3' SHA256: 84e68831ca2cd0109d3bbc96c8fe44acbadfe11782814e63aca06db0c2b57a44
Shader 'CanvasOcclusionShaderGLES3' SHA256: f2134254e8dfb198e9f716b8610b94c697fd12759d778684de0ba145f9d4bb3a
Shader 'SceneShaderGLES3' SHA256: 5d0c642a5e4f7c71e9dffcfc4fe2d218afffb9440452b03903630c5b8e583b21
Shader 'SkyShaderGLES3' SHA256: 09a220754af11439d08884ff7dc0332c6aed73e24260f39ea396c67eb3cd250b
OpenGL API 3.3.0 NVIDIA 610.57.04 - Compatibility - Using Device: NVIDIA - NVIDIA GeForce RTX 2070
PulseAudio 17.0.0 detected.
PulseAudio: context other
PulseAudio: context other
PulseAudio: context other
PulseAudio: context ready
PulseAudio: Detecting channels for device: auto_null
PulseAudio: detected 2 output channels
PulseAudio: audio buffer frames: 512 calculated output latency: 11ms

TextServer: Primary interface set to: "ICU / HarfBuzz / Graphite (Built-in)".
CORE API HASH: 75400357
EDITOR API HASH: 3012763406
SceneTreeFTI: traversal method DEFAULT
Loading resource: /home/mytruelove/.config/godot/editor_settings-4.6.tres
EditorSettings: Load OK!
EditorTheme: Generating new theme for the config '3810048042'.
EditorTheme: Generating new icons.
EditorTheme: Generating new fonts.
EditorTheme: Generating new styles.
PortalDesktop: org.freedesktop.portal.FileChooser version 4 detected, version 3 required.
PortalDesktop: org.freedesktop.portal.Settings version 2 detected, version 1 required.
Devices:
  #0: Intel Intel(R) HD Graphics 530 (SKL GT2) - Unsupported, Integrated
  #1: NVIDIA NVIDIA GeForce RTX 2070 - Unsupported, Discrete
  #2: Unknown llvmpipe (LLVM 22.1.8, 256 bits) - Unsupported, CPU
Optional extension VK_EXT_fragment_density_map not found
Optional extension VK_QCOM_fragment_density_map_offset not found
Optional extension VK_EXT_astc_decode_mode not found
Optional extension VK_EXT_texture_compression_astc_hdr not found
Optional extension VK_EXT_debug_marker not found
- Vulkan Fragment Shading Rate supported:
  Pipeline fragment shading rate
  Primitive fragment shading rate
  Attachment fragment shading rate, min texel size: (16, 16), max texel size: (16, 16), max fragment size: (4, 4)
- Vulkan Fragment Density Map not supported
- Vulkan multiview supported:
  max view count: 32
  max instances: 134217727
- Vulkan subgroup:
  size: 32
  min size: 32
  max size: 32
  stages: STAGE_VERTEX, STAGE_TESSELLATION_CONTROL, STAGE_TESSELLATION_EVALUATION, STAGE_GEOMETRY, STAGE_FRAGMENT, STAGE_COMPUTE, STAGE_RAYGEN_KHR, STAGE_ANY_HIT_KHR, STAGE_CLOSEST_HIT_KHR, STAGE_MISS_KHR, STAGE_INTERSECTION_KHR, STAGE_CALLABLE_KHR, STAGE_TASK_NV, STAGE_MESH_NV
  supported ops: FEATURE_BASIC, FEATURE_VOTE, FEATURE_ARITHMETIC, FEATURE_BALLOT, FEATURE_SHUFFLE, FEATURE_SHUFFLE_RELATIVE, FEATURE_CLUSTERED, FEATURE_QUAD, FEATURE_PARTITIONED_NV
  quad operations in all stages
Loading resource: /home/mytruelove/.cache/godot/editor_doc_cache-4.6.res
Loaded system CA certificates
PortalDesktop: org.freedesktop.portal.Screenshot version 2 detected, version 1 required.
FreeDesktopScreenSaver: Released screensaver inhibition cookie: 1755907198
Script documentation cache not found. Regenerating it may take a while for projects with many scripts.
Loading resource: res://addons/hermes_editor/plugin.gd
Loading resource: res://scenes/Main.tscn
Loading resource: res://scenes/DragonAvatar3D.tscn
Loading resource: res://scripts/DragonAvatar3D.gd
Loading resource: res://assets/dragon_3d_frames.tres
Loading resource: res://assets/idle_flap.png
Loading resource: res://.godot/imported/idle_flap.png-20dbcbc6cb859f02a92d0afa26ddaaa1.s3tc.ctex
Loading resource: res://scripts/EngAInBridge3D.gd
Loading resource: res://scenes/ControlHUD.tscn
Loading resource: res://scripts/ControlHUD.gd
Loading resource: res://scripts/Main.gd
Loading resource: res://addons/godot_ollama_task_performer/assist_dock.gd
Generated 'res://addons/godot_ollama_task_performer/assist_dock.tscn' preview in 22 usec
Generated 'res://addons/godot_ollama_task_performer/plugin.cfg' preview in 49 usec
Generated 'res://addons/godot_ollama_task_performer/README.md' preview in 51 usec
Generated 'res://addons/hermes_editor/plugin.cfg' preview in 46 usec
Generated 'res://addons/hermes_editor/README.md' preview in 50 usec
Generated 'res://assets/dragon_3d_frames.tres' preview in 51 usec
Generated 'res://evidence/stage8_ticket3f_green.txt' preview in 60 usec
Generated 'res://scenes/ControlHUD.tscn' preview in 12 usec
Generated 'res://scenes/DragonAvatar3D.tscn' preview in 9 usec
Generated 'res://scenes/Main.tscn' preview in 2519 usec
Generated 'res://snapshots/perception_cap_1b7e909b99d3ee111bec660311e32b95_1.json' preview in 55 usec
Generated 'res://snapshots/perception_cap_3adeef61cc885c35200be389b975c8d9_1.json' preview in 45 usec
Generated 'res://snapshots/perception_cap_5b4aef15ce8a040f5c6e28fe99085c0c_1.json' preview in 47 usec
Generated 'res://snapshots/perception_cap_5b8faf517ccd9864fee44e0f1ad82e58_4.json' preview in 46 usec
Generated 'res://snapshots/perception_cap_7fb5fcf92d5b65025c9dfe69487253e3_3.json' preview in 43 usec
Generated 'res://snapshots/perception_cap_803b5b45ecf5aab8915a05525b36570a_1.json' preview in 45 usec
Generated 'res://snapshots/perception_cap_2781f02ee0141c664a2b107ec6477866_1.json' preview in 44 usec
Generated 'res://snapshots/perception_cap_a90f03da75879203c04e842d5e8109f4_2.json' preview in 55 usec
Generated 'res://snapshots/perception_cap_cb1d91386b9fb24a1f969d439664566e_1.json' preview in 44 usec
Generated 'res://snapshots/perception_cap_d5a08b067a33d2d8168973f5be2454c8_2.json' preview in 47 usec
Generated 'res://snapshots/perception_cap_f4878cd2d2af2a0cc566800892f6daa6_1.json' preview in 43 usec
Generated 'res://snapshots/perception_cap_ffe06c9aedc9f92592ce15142543aad8_1.json' preview in 64 usec
Generated 'res://DRAGON_SCENE_UNDERSTANDING_CHANNELS.md' preview in 44 usec
Generated 'res://engain_request.json' preview in 71 usec
Generated 'res://README.md' preview in 50 usec
Generated 'ID:-9223372014541077686' preview in 8 usec
Generated 'ID:-9223372012561365686' preview in 8 usec
Generated 'ID:-9223372012779469507' preview in 3 usec
Loading resource: res://addons/godot_ollama_task_performer/plugin.gd
Loading resource: res://addons/godot_ollama_task_performer/assist_dock.tscn
Loading resource: res://addons/hermes_editor/_teardown_case1_completed_then_freed.gd
Loading resource: res://addons/hermes_editor/_teardown_case2_stop_mid_turn.gd
Loading resource: res://addons/hermes_editor/_teardown_case3_freed_mid_turn.gd
Loading resource: res://addons/hermes_editor/live_teardown_proof.gd
Loading resource: res://addons/hermes_editor/test_hermes_bridge_logic.gd
Loading resource: res://tests/transcript_visibility_boundary.gd

