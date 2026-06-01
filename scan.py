import requests
import sys
import os
import time

def scan_security(file_path):
    # 1. 파일 존재 여부 및 경로 확인
    if not os.path.exists(file_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다 -> {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 실패: {e}")
        return

    # 2. Ollama API 설정
    url = "http://localhost:11434/api/generate"
    
    prompt_text = f"""당신은 15년 경력의 시니어 보안 감사관(Security Auditor)입니다. 다음 소스 코드를 CWE(Common Weakness Enumeration) 및 OWASP Top 10 기준에 따라 정밀 분석해 주세요.

분석 시 다음 규칙을 엄수하세요:

1. 취약점 분류: 취약점 명칭과 CWE 번호를 명시할 것.
2. 위험도: High, Medium, Low로 구분할 것.
3. 공격 시나리오: 해커가 이 취약점을 어떻게 악용할 수 있는지 짧게 설명할 것.
4. 수정 방안: 보안 코딩 규칙이 적용된 '수정된 코드 스니펫'을 반드시 포함할 것.
5. 언어: 한국어로 답변할 것

[분석할 소스 코드]
{code_content}"""

    payload = {
        "model": "deepseek-coder-v2:16b", 
        "prompt": prompt_text,
        "stream": False
    }

    print(f"🔍 진단 시작: {file_path}...")
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json().get("response")
        
        base_name = os.path.basename(file_path)
        report_file = f"{base_name}_scan_result.txt"
        
        with open(report_file, "w", encoding="utf-8") as rf:
            rf.write(f"🛡️  [{file_path}] 보안 진단 결과\n")
            rf.write("="*50 + "\n")
            rf.write(result if result else "결과가 없습니다.")
            rf.write("\n" + "="*50 + "\n")
            
        print(f"✅ 진단 완료! 결과가 '{report_file}' 파일에 저장되었습니다.")
        
    except requests.exceptions.Timeout:
        print("❌ 오류: 응답 시간이 5분(300초)을 초과하여 실행이 중단되었습니다.")
    except requests.exceptions.ConnectionError:
        print("❌ 오류: Ollama 서버가 실행 중이지 않습니다. 'ollama serve'를 확인하세요.")
    except Exception as e:
        print(f"❌ API 호출 중 오류 발생: {e}")

if __name__ == "__main__":
    # 실행 시 파라미터가 있는지 확인 (파일명 포함이므로 2개 이상이어야 함)
    if len(sys.argv) < 2:
        print("💡 사용법: python scan.py [대상_파일_경로]")
        print("예시: python scan.py ./src/auth.py")
    else:
        # 첫 번째 파라미터를 파일 경로로 지정
        target_path = sys.argv[1]
        
        start_time = time.time()
        scan_security(target_path)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        print(f"\n⏱️  총 소요 시간: {elapsed_time:.2f}초")