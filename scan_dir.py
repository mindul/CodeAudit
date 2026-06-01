import requests
import sys
import os
import glob
import time

def scan_file(file_path, model_name):
    """개별 파일을 분석하는 함수"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
    except Exception as e:
        return f"파일 읽기 실패: {e}"

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
        "model": model_name,
        "prompt": prompt_text,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=300) # 5분 타임아웃
        response.raise_for_status()
        return response.json().get("response")
    except Exception as e:
        return f"분석 중 오류 발생: {e}"

def main():
    if len(sys.argv) < 2:
        print("💡 사용법: python scan_dir.py [디렉토리_경로]")
        return

    target_dir = sys.argv[1]
    # 모델명은 사양에 맞춰 lite 버전 권장
    #model_name = "deepseek-coder-v2:lite" 
    model_name = "deepseek-coder-v2:16b"
    
    if not os.path.isdir(target_dir):
        print(f"❌ 오류: '{target_dir}'은(는) 유효한 디렉토리가 아닙니다.")
        return

    # 분석할 확장자 지정 (예: .py, .c, .java, .js 등)
    extensions = ['*.py', '*.js', '*.java', '*.c', "*.php"]
    files_to_scan = []
    for ext in extensions:
        files_to_scan.extend(glob.glob(os.path.join(target_dir, ext)))

    if not files_to_scan:
        print("📁 분석할 소스 파일이 없습니다.")
        return

    print(f"🚀 총 {len(files_to_scan)}개의 파일을 찾았습니다. 분석을 시작합니다...")
    
    start_time = time.time()
    
    # 결과 저장을 위한 폴더 생성
    report_dir = "scan_reports"
    os.makedirs(report_dir, exist_ok=True)

    for i, file_path in enumerate(files_to_scan, 1):
        file_name = os.path.basename(file_path)
        print(f"[{i}/{len(files_to_scan)}] 분석 중: {file_name}...")
        
        result = scan_file(file_path, model_name)
        
        # 결과를 파일로 저장
        report_path = os.path.join(report_dir, f"{file_name}_report.txt")
        with open(report_path, "w", encoding="utf-8") as rf:
            rf.write(f"--- File: {file_path} ---\n\n")
            rf.write(result)
        
        print(f"✅ 완료! 리포트 저장됨: {report_path}")

    print(f"\n✨ 모든 분석이 완료되었습니다. '{report_dir}' 폴더를 확인하세요.")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"⏱️  총 소요 시간: {elapsed_time:.2f}초")

if __name__ == "__main__":
    main()