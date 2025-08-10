"""
운영 관리 시스템
A2A(Application-to-Application) 및 ADK(Application Development Kit) 기반 운영 관리
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import threading
import time

logger = logging.getLogger(__name__)


class OperationalManager:
    """운영 관리 시스템"""

    def __init__(self):
        self.db_path = "data/qa_radar.db"
        self.results_dir = Path("results")
        self.logs_dir = Path("logs")

        # 디렉토리 생성
        self.results_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)

        # 데이터베이스 초기화
        self._init_database()

        # 운영 설정
        self.operational_config = {
            "auto_cleanup_days": 30,
            "max_concurrent_tests": 5,
            "notification_enabled": True,
            "dashboard_refresh_interval": 60,  # 초
            "backup_enabled": True,
            "backup_interval_hours": 24,
        }

        # 백그라운드 작업 시작
        self._start_background_tasks()

    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 테스트 결과 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    execution_time REAL,
                    quality_score REAL,
                    screenshots TEXT,
                    logs TEXT,
                    healing_actions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 품질 메트릭 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    performance_score REAL,
                    accessibility_score REAL,
                    seo_score REAL,
                    functionality_score REAL,
                    overall_score REAL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES test_results (test_id)
                )
            """
            )

            # 운영 로그 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS operational_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    test_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # 알림 테이블
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    test_id TEXT,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            conn.close()

            logger.info("데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")

    def _start_background_tasks(self):
        """백그라운드 작업 시작"""
        # 자동 정리 작업
        cleanup_thread = threading.Thread(target=self._cleanup_old_data, daemon=True)
        cleanup_thread.start()

        # 백업 작업
        if self.operational_config["backup_enabled"]:
            backup_thread = threading.Thread(target=self._backup_data, daemon=True)
            backup_thread.start()

        logger.info("백그라운드 작업 시작")

    async def save_test_result(self, test_result):
        """테스트 결과 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 테스트 결과 저장
            cursor.execute(
                """
                INSERT OR REPLACE INTO test_results 
                (test_id, url, status, execution_time, quality_score, screenshots, logs, healing_actions, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    test_result.test_id,
                    "",  # URL은 별도로 저장 필요
                    test_result.status,
                    test_result.execution_time,
                    test_result.quality_score,
                    json.dumps(test_result.screenshots),
                    json.dumps(test_result.logs),
                    json.dumps(test_result.healing_actions),
                    datetime.now(),
                ),
            )

            # 품질 메트릭 저장
            cursor.execute(
                """
                INSERT INTO quality_metrics 
                (test_id, overall_score, created_at)
                VALUES (?, ?, ?)
            """,
                (test_result.test_id, test_result.quality_score, datetime.now()),
            )

            conn.commit()
            conn.close()

            # 결과 파일 저장
            await self._save_result_file(test_result)

            # 알림 생성
            await self._create_notification(test_result)

            logger.info(f"테스트 결과 저장 완료: {test_result.test_id}")

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")

    async def save_test_error(self, test_id: str, error_message: str):
        """테스트 오류 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO test_results 
                (test_id, url, status, execution_time, quality_score, screenshots, logs, healing_actions, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    test_id,
                    "",
                    "failed",
                    0.0,
                    0.0,
                    json.dumps([]),
                    json.dumps([error_message]),
                    json.dumps([]),
                    datetime.now(),
                ),
            )

            conn.commit()
            conn.close()

            # 오류 알림 생성
            await self._create_error_notification(test_id, error_message)

            logger.info(f"테스트 오류 저장 완료: {test_id}")

        except Exception as e:
            logger.error(f"테스트 오류 저장 실패: {e}")

    async def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """테스트 상태 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM test_results WHERE test_id = ?
            """,
                (test_id,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "test_id": row[1],
                    "status": row[3],
                    "execution_time": row[4],
                    "quality_score": row[5],
                    "screenshots": json.loads(row[6]) if row[6] else [],
                    "logs": json.loads(row[7]) if row[7] else [],
                    "healing_actions": json.loads(row[8]) if row[8] else [],
                    "created_at": row[9],
                    "updated_at": row[10],
                }
            else:
                return {"error": "테스트를 찾을 수 없습니다"}

        except Exception as e:
            logger.error(f"테스트 상태 조회 실패: {e}")
            return {"error": str(e)}

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드 데이터 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 최근 7일간 통계
            seven_days_ago = datetime.now() - timedelta(days=7)

            # 총 테스트 수
            cursor.execute(
                """
                SELECT COUNT(*) FROM test_results 
                WHERE created_at >= ?
            """,
                (seven_days_ago,),
            )
            total_tests = cursor.fetchone()[0]

            # 성공한 테스트 수
            cursor.execute(
                """
                SELECT COUNT(*) FROM test_results 
                WHERE status = 'completed' AND created_at >= ?
            """,
                (seven_days_ago,),
            )
            successful_tests = cursor.fetchone()[0]

            # 평균 품질 점수
            cursor.execute(
                """
                SELECT AVG(quality_score) FROM test_results 
                WHERE quality_score > 0 AND created_at >= ?
            """,
                (seven_days_ago,),
            )
            avg_quality = cursor.fetchone()[0] or 0

            # 최근 테스트 결과
            cursor.execute(
                """
                SELECT test_id, status, quality_score, created_at 
                FROM test_results 
                ORDER BY created_at DESC 
                LIMIT 10
            """
            )
            recent_tests = cursor.fetchall()

            # 품질 트렌드 (일별)
            cursor.execute(
                """
                SELECT DATE(created_at) as date, AVG(quality_score) as avg_score
                FROM test_results 
                WHERE quality_score > 0 AND created_at >= ?
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            """,
                (seven_days_ago,),
            )
            quality_trends = cursor.fetchall()

            # 미읽 알림 수
            cursor.execute(
                """
                SELECT COUNT(*) FROM notifications WHERE is_read = FALSE
            """
            )
            unread_notifications = cursor.fetchone()[0]

            conn.close()

            return {
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "success_rate": (
                        (successful_tests / total_tests * 100) if total_tests > 0 else 0
                    ),
                    "average_quality": round(avg_quality, 2),
                    "unread_notifications": unread_notifications,
                },
                "recent_tests": [
                    {
                        "test_id": row[0],
                        "status": row[1],
                        "quality_score": row[2],
                        "created_at": row[3],
                    }
                    for row in recent_tests
                ],
                "quality_trends": [
                    {"date": row[0], "average_score": round(row[1], 2)}
                    for row in quality_trends
                ],
            }

        except Exception as e:
            logger.error(f"대시보드 데이터 조회 실패: {e}")
            return {"error": str(e)}

    async def get_quality_report(
        self, test_id: str = None, days: int = 30
    ) -> Dict[str, Any]:
        """품질 보고서 생성"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if test_id:
                # 특정 테스트의 품질 보고서
                cursor.execute(
                    """
                    SELECT * FROM quality_metrics WHERE test_id = ?
                """,
                    (test_id,),
                )
                row = cursor.fetchone()

                if row:
                    return {
                        "test_id": test_id,
                        "overall_score": row[5],
                        "details": json.loads(row[6]) if row[6] else {},
                        "created_at": row[7],
                    }
                else:
                    return {"error": "품질 메트릭을 찾을 수 없습니다"}
            else:
                # 기간별 품질 보고서
                start_date = datetime.now() - timedelta(days=days)

                cursor.execute(
                    """
                    SELECT 
                        AVG(overall_score) as avg_score,
                        MIN(overall_score) as min_score,
                        MAX(overall_score) as max_score,
                        COUNT(*) as total_tests
                    FROM quality_metrics 
                    WHERE created_at >= ?
                """,
                    (start_date,),
                )

                row = cursor.fetchone()

                # 카테고리별 평균 점수
                cursor.execute(
                    """
                    SELECT 
                        AVG(performance_score) as avg_performance,
                        AVG(accessibility_score) as avg_accessibility,
                        AVG(seo_score) as avg_seo,
                        AVG(functionality_score) as avg_functionality
                    FROM quality_metrics 
                    WHERE created_at >= ?
                """,
                    (start_date,),
                )

                category_row = cursor.fetchone()

                conn.close()

                return {
                    "period": f"최근 {days}일",
                    "summary": {
                        "average_score": round(row[0] or 0, 2),
                        "minimum_score": round(row[1] or 0, 2),
                        "maximum_score": round(row[2] or 0, 2),
                        "total_tests": row[3] or 0,
                    },
                    "category_scores": {
                        "performance": round(category_row[0] or 0, 2),
                        "accessibility": round(category_row[1] or 0, 2),
                        "seo": round(category_row[2] or 0, 2),
                        "functionality": round(category_row[3] or 0, 2),
                    },
                }

        except Exception as e:
            logger.error(f"품질 보고서 생성 실패: {e}")
            return {"error": str(e)}

    async def _save_result_file(self, test_result):
        """결과 파일 저장"""
        try:
            result_file = self.results_dir / f"{test_result.test_id}.json"

            result_data = {
                "test_id": test_result.test_id,
                "status": test_result.status,
                "execution_time": test_result.execution_time,
                "quality_score": test_result.quality_score,
                "screenshots": test_result.screenshots,
                "logs": test_result.logs,
                "healing_actions": test_result.healing_actions,
                "created_at": datetime.now().isoformat(),
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            logger.info(f"결과 파일 저장 완료: {result_file}")

        except Exception as e:
            logger.error(f"결과 파일 저장 실패: {e}")

    async def _create_notification(self, test_result):
        """알림 생성"""
        try:
            if not self.operational_config["notification_enabled"]:
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 품질 점수에 따른 알림
            if test_result.quality_score < 70:
                notification_type = "warning"
                title = "품질 점수 경고"
                message = f"테스트 {test_result.test_id}의 품질 점수가 낮습니다: {test_result.quality_score:.1f}/100"
            elif test_result.quality_score >= 90:
                notification_type = "success"
                title = "품질 점수 우수"
                message = f"테스트 {test_result.test_id}의 품질 점수가 우수합니다: {test_result.quality_score:.1f}/100"
            else:
                notification_type = "info"
                title = "테스트 완료"
                message = f"테스트 {test_result.test_id}가 완료되었습니다: {test_result.quality_score:.1f}/100"

            cursor.execute(
                """
                INSERT INTO notifications (type, title, message, test_id)
                VALUES (?, ?, ?, ?)
            """,
                (notification_type, title, message, test_result.test_id),
            )

            conn.commit()
            conn.close()

            logger.info(f"알림 생성 완료: {notification_type}")

        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")

    async def _create_error_notification(self, test_id: str, error_message: str):
        """오류 알림 생성"""
        try:
            if not self.operational_config["notification_enabled"]:
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notifications (type, title, message, test_id)
                VALUES (?, ?, ?, ?)
            """,
                (
                    "error",
                    "테스트 실패",
                    f"테스트 {test_id} 실행 중 오류 발생: {error_message}",
                    test_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"오류 알림 생성 실패: {e}")

    def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        while True:
            try:
                cleanup_days = self.operational_config["auto_cleanup_days"]
                cutoff_date = datetime.now() - timedelta(days=cleanup_days)

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # 오래된 테스트 결과 삭제
                cursor.execute(
                    """
                    DELETE FROM test_results 
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                # 오래된 품질 메트릭 삭제
                cursor.execute(
                    """
                    DELETE FROM quality_metrics 
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                # 오래된 운영 로그 삭제
                cursor.execute(
                    """
                    DELETE FROM operational_logs 
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                # 읽은 알림 삭제 (7일 이상)
                read_cutoff = datetime.now() - timedelta(days=7)
                cursor.execute(
                    """
                    DELETE FROM notifications 
                    WHERE is_read = TRUE AND created_at < ?
                """,
                    (read_cutoff,),
                )

                conn.commit()
                conn.close()

                logger.info(f"오래된 데이터 정리 완료 (기준: {cleanup_days}일)")

                # 24시간 대기
                time.sleep(24 * 60 * 60)

            except Exception as e:
                logger.error(f"데이터 정리 중 오류: {e}")
                time.sleep(60 * 60)  # 1시간 대기

    def _backup_data(self):
        """데이터 백업"""
        while True:
            try:
                backup_interval = self.operational_config["backup_interval_hours"]

                # 백업 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backups/qa_radar_backup_{timestamp}.db"

                # 백업 디렉토리 생성
                Path("backups").mkdir(exist_ok=True)

                # 데이터베이스 백업
                import shutil

                shutil.copy2(self.db_path, backup_path)

                logger.info(f"데이터 백업 완료: {backup_path}")

                # 백업 간격만큼 대기
                time.sleep(backup_interval * 60 * 60)

            except Exception as e:
                logger.error(f"데이터 백업 중 오류: {e}")
                time.sleep(60 * 60)  # 1시간 대기

    async def get_notifications(
        self, unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """알림 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if unread_only:
                cursor.execute(
                    """
                    SELECT * FROM notifications 
                    WHERE is_read = FALSE 
                    ORDER BY created_at DESC
                """
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM notifications 
                    ORDER BY created_at DESC 
                    LIMIT 50
                """
                )

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "message": row[3],
                    "test_id": row[4],
                    "is_read": bool(row[5]),
                    "created_at": row[6],
                }
                for row in rows
            ]

        except Exception as e:
            logger.error(f"알림 조회 실패: {e}")
            return []

    async def mark_notification_read(self, notification_id: int):
        """알림 읽음 표시"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE notifications 
                SET is_read = TRUE 
                WHERE id = ?
            """,
                (notification_id,),
            )

            conn.commit()
            conn.close()

            logger.info(f"알림 읽음 표시 완료: {notification_id}")

        except Exception as e:
            logger.error(f"알림 읽음 표시 실패: {e}")

    def log_operational_event(self, level: str, message: str, test_id: str = None):
        """운영 이벤트 로깅"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO operational_logs (level, message, test_id)
                VALUES (?, ?, ?)
            """,
                (level, message, test_id),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"운영 이벤트 로깅 실패: {e}")
