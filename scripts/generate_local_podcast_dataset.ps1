param(
    [string]$DatasetDir = "media-dataset"
)

$ErrorActionPreference = "Stop"
$target = Join-Path (Resolve-Path $DatasetDir) "podcast"
New-Item -ItemType Directory -Force -Path $target | Out-Null

$items = @(
    @{ title="Slow breathing for one minute"; category="relax"; text="Sit comfortably. Breathe in slowly for four counts. Pause briefly. Breathe out for six counts. Repeat at a pace that feels comfortable." },
    @{ title="Name the feeling"; category="sad_support"; text="You do not need to solve everything right now. Try naming what is present. Sadness, stress, tiredness, or uncertainty. Noticing it is already a small step." },
    @{ title="Start a focus session"; category="focus"; text="Choose the smallest task you can finish in five minutes. Put away distractions. Begin with one breath and one simple action." },
    @{ title="Rest before sleep"; category="sleep"; text="Today has been long enough. Relax your shoulders and jaw. Let your breathing slow down. You do not need to do anything else for the next few minutes." },
    @{ title="Keep positive energy"; category="happy"; text="Notice one thing that felt good today. You can share that small joy or keep it as a reminder that something good happened." },
    @{ title="Cool down anger"; category="anger_release"; text="When emotion is strong, pause before reacting. Put both feet on the floor. Let each exhale be longer than the inhale and give your body a safe moment to settle." },
    @{ title="Restore your energy"; category="energy_recover"; text="Start with water, a comfortable posture, and one very small task. Recovery does not need to be fast. Your body can return to its rhythm step by step." },
    @{ title="Return to the present"; category="relax"; text="Look around and name three things you can see. Feel where your body is supported. You are here in this moment and you can slow down." },
    @{ title="Take a gentle break"; category="focus"; text="Look away from the screen for a few minutes. Relax your shoulders and take a sip of water. Then return to your work with a new rhythm." },
    @{ title="Speak kindly to yourself"; category="sad_support"; text="Try a sentence you would say to a good friend. I am doing my best in this situation. I am allowed to rest for a moment." }
)

$items += @(
    @{ title="A two-minute reset"; category="relax"; text="Pause where you are. Unclench your hands. Let your shoulders fall and take three slow breaths. Nothing else needs your attention for these two minutes." },
    @{ title="Make room for sadness"; category="sad_support"; text="Sadness can be present without becoming the whole day. Place one hand on your chest. Breathe gently and allow yourself a little patience." },
    @{ title="Plan one focused block"; category="focus"; text="Choose one task and set a short timer. When the timer starts, give that task your full attention. A small completed block is real progress." },
    @{ title="A softer evening"; category="sleep"; text="Dim the lights if you can. Put down the next task. Let your body know that the day is becoming quieter and rest is welcome." },
    @{ title="Celebrate a small win"; category="happy"; text="Think of one choice you made well today. Let yourself notice the effort behind it. Small wins deserve a moment of recognition." },
    @{ title="Pause before replying"; category="anger_release"; text="If you feel heat rising, wait for one long exhale before you respond. This pause is not weakness. It gives you room to choose your next words." },
    @{ title="Move with gentle energy"; category="energy_recover"; text="Roll your shoulders and stretch your arms. A little movement can tell your body that energy is returning. Keep the next step very small." },
    @{ title="Five senses grounding"; category="relax"; text="Notice five things you can see, four things you can feel, three sounds, two scents, and one taste. Let the present moment become clear again." },
    @{ title="Close a distracting loop"; category="focus"; text="Write down the thought that keeps interrupting you. You do not need to solve it now. Put it on the list and return to the task in front of you." },
    @{ title="Permission to pause"; category="sad_support"; text="You are allowed to take a break before you feel fully ready. Rest can be part of moving forward, not a delay from it." },
    @{ title="Settle your body"; category="relax"; text="Feel both feet on the floor. Soften your jaw and lower your shoulders. With each breath, let the chair or ground support a little more of your weight." },
    @{ title="One clear priority"; category="focus"; text="Ask yourself which one thing matters most in the next hour. Name it simply. Let the other tasks wait while you give that priority a calm start." },
    @{ title="Let the day end"; category="sleep"; text="Notice that you have done enough for today. Put tomorrow's tasks somewhere safe on a list and allow your mind to release them for the night." },
    @{ title="Share good energy"; category="happy"; text="Send a kind message, smile at someone, or remember a moment of connection. Positive energy becomes stronger when you give it a small place to go." },
    @{ title="Release the tightness"; category="anger_release"; text="Breathe in through your nose and exhale slowly through your mouth. Imagine the tension leaving your hands, shoulders, and forehead one area at a time." },
    @{ title="Recover at your pace"; category="energy_recover"; text="You do not have to feel fully energetic before beginning. Drink some water, sit comfortably, and start with the easiest next action." },
    @{ title="A calm transition"; category="relax"; text="Before changing activities, take one breath and notice what you are leaving behind. Then name the next place you want to put your attention." },
    @{ title="Focus after a setback"; category="focus"; text="A difficult moment does not cancel your plans. Choose one practical action that helps you re-enter the work, even if it takes only two minutes." },
    @{ title="Prepare for quiet sleep"; category="sleep"; text="Let your breath become a little slower than before. Imagine your room becoming calm, safe, and free from anything you need to fix tonight." },
    @{ title="Notice what is working"; category="happy"; text="Look for one part of your day that is already okay. It may be small, but paying attention to it can bring balance to the bigger picture." },
    @{ title="Choose a gentle response"; category="anger_release"; text="You can feel angry and still choose a response that protects you. Take a breath, create distance if possible, and return when your body is calmer." },
    @{ title="Recharge with kindness"; category="energy_recover"; text="Treat low energy as information, not a failure. Offer yourself water, food, movement, or a few quiet minutes before asking for more effort." },
    @{ title="Anchor in the room"; category="relax"; text="Look at one steady object in the room. Notice its colour and shape. Let your breathing settle while your attention rests on something simple." },
    @{ title="Begin without pressure"; category="focus"; text="You do not need the perfect plan to begin. Open the document, gather the materials, and take the first visible step with no extra pressure." },
    @{ title="Ease into rest"; category="sleep"; text="Release your hands, then your arms, then your shoulders. Let the next exhale be slow. Rest can begin with one small signal from your body." },
    @{ title="Keep your momentum"; category="happy"; text="If something is going well, notice the conditions that helped. Carry one of them into your next activity and let that good rhythm continue." },
    @{ title="Make space before action"; category="anger_release"; text="When you want to act quickly, make space first. Count slowly to five, feel the ground, and decide what response will serve you best." },
    @{ title="Return energy slowly"; category="energy_recover"; text="Energy can return in waves. Meet the current wave with one useful action, then pause again. Steady recovery is still recovery." },
    @{ title="A mindful minute"; category="relax"; text="For one minute, notice your breath without changing it. When your thoughts move away, gently return to the feeling of air moving in and out." },
    @{ title="Finish the next step"; category="focus"; text="Do not measure the whole project right now. Identify the next visible step, finish it, and let completion create the motivation for what comes after." }
)

Add-Type -AssemblyName System.Speech
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.Rate = -1
$catalog = @()
for ($i = 0; $i -lt $items.Count; $i++) {
    $item = $items[$i]
    $name = "{0:D2}-emoticare-guidance" -f ($i + 1)
    $wav = Join-Path $target "$name.wav"
    $mp3 = Join-Path $target "$name.mp3"
    $voice.SetOutputToWaveFile($wav)
    $voice.Speak($item.text)
    $voice.SetOutputToDefaultAudioDevice()
    & ffmpeg -y -loglevel error -i $wav -codec:a libmp3lame -b:a 128k $mp3
    Remove-Item -LiteralPath $wav
    $catalog += @{ media_type="podcast"; title=$item.title; creator="EmotiCare Local Guidance"; category=$item.category; duration_sec=45; source_url="/media/podcast/$name.mp3"; dataset="EmotiCare Local Spoken Dataset v1"; license_note="Project-created audio; no external URL stored." }
}
$catalog | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path (Resolve-Path $DatasetDir) "podcast_catalog.json") -Encoding utf8
Write-Output "Generated $($items.Count) local podcast clips."
