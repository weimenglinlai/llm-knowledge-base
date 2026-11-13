# LLM Knowledge Base

Knowledge base construction, agent integration and a web frontend for LLM applications.

## Structure

```
COZE_AGENT.md
anythingLLM/LICENSE.electron.txt
anythingLLM/vk_swiftshader_icd.json
build_kb.py
capture_ui.py
configure_allm.py
coze_test_results.json
extract_frontend.js
fill_report.py
fix_layout.py
frontend/assistant.html
frontend/index.html
frontend/magic-beacon.html
frontend/magicecho.html
frontend/vad/vad.worklet.bundle.min.js
grab_win.py
qa_results.json
run_allm_server.sh
run_collector.sh
run_ollama.sh
serve_frontend.js
shot_electron.py
shot_ollama.py
sse_client.py
start_all.sh
test_qa.py
tools/dl.html
```

## Setup

Install dependencies from `requirements.txt` when present:

```bash
pip install -r requirements.txt
```

Data files, model weights and generated outputs are not included; place them under the paths referenced by the configuration before running.
