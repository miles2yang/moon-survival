"""
Moon Survival Experiment Task
一個團隊決策和優先級排序的遊戲/實驗

玩家需要根據月球生存的優先級來排序物品。
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class Item:
    """月球倖存物品"""
    name: str
    official_rank: int  # NASA 專家的排名
    description: str


class MoonSurvivalExperiment:
    """月球倖存實驗"""
    
    # NASA 專家的官方排名
    OFFICIAL_ITEMS = [
        Item("氧氣瓶", 1, "呼吸"),
        Item("水", 2, "補充液體"),
        Item("星圖", 3, "導航"),
        Item("食物濃縮物", 4, "營養"),
        Item("太陽能電池板", 5, "電力"),
        Item("衣服補丁", 6, "防止失壓"),
        Item("醫療箱", 7, "急救"),
        Item("繩索", 8, "安全/移動"),
        Item("降落傘", 9, "防止隕石碰撞"),
        Item("救生筏", 10, "隱蔽所"),
        Item("信號鏡", 11, "通信"),
        Item("手電筒", 12, "照明"),
        Item("火柴", 13, "點火"),
        Item("月球地圖", 14, "導航輔助"),
        Item("磁羅盤", 15, "導航（不太有效）"),
    ]
    
    def __init__(self):
        """初始化實驗"""
        self.items = self.OFFICIAL_ITEMS.copy()
        self.team_ranking: List[Item] = []
        self.individual_rankings: Dict[str, List[Item]] = {}
    
    def display_items(self) -> None:
        """顯示所有物品"""
        print("=" * 60)
        print("月球倖存實驗 - 物品列表")
        print("=" * 60)
        print("\n你被困在月球上，距離基地 200 英里。")
        print("你的太空船損壞了。")
        print("請根據倖存重要性排序以下 15 項物品（最重要到最不重要）:\n")
        
        for i, item in enumerate(self.items, 1):
            print(f"{i:2d}. {item.name:20s} - {item.description}")
        print()
    
    def get_individual_ranking(self, person_name: str) -> None:
        """獲取個人排名"""
        print(f"\n{person_name}，請為以下物品排序（輸入物品編號，用逗號分隔）:")
        print("例如: 1,3,5,2,4,6,7,8,9,10,11,12,13,14,15")
        
        while True:
            try:
                ranking_input = input(f"{person_name} 的排序: ")
                indices = [int(x.strip()) - 1 for x in ranking_input.split(",")]
                
                # 驗證輸入
                if len(indices) != len(self.items):
                    print(f"❌ 錯誤: 請輸入 {len(self.items)} 個物品")
                    continue
                
                if sorted(indices) != list(range(len(self.items))):
                    print("❌ 錯誤: 每個物品必須恰好出現一次")
                    continue
                
                self.individual_rankings[person_name] = [self.items[i] for i in indices]
                print("✅ 排序已保存\n")
                break
                
            except ValueError:
                print("❌ 輸入無效，請重試")
    
    def calculate_team_ranking(self) -> None:
        """計算團隊平均排名"""
        if not self.individual_rankings:
            print("❌ 沒有個人排名資料")
            return
        
        # 計算每項物品的平均排名
        item_scores = {}
        for item in self.items:
            scores = []
            for person_ranking in self.individual_rankings.values():
                rank = next((i + 1 for i, x in enumerate(person_ranking) if x.name == item.name), 0)
                scores.append(rank)
            item_scores[item.name] = sum(scores) / len(scores)
        
        # 按平均排名排序
        self.team_ranking = sorted(
            self.items,
            key=lambda item: item_scores[item.name]
        )
    
    def display_results(self) -> None:
        """顯示結果比較"""
        print("\n" + "=" * 80)
        print("結果比較")
        print("=" * 80)
        
        # 顯示團隊排名
        print("\n【團隊排名（平均）】")
        print("-" * 80)
        for rank, item in enumerate(self.team_ranking, 1):
            print(f"{rank:2d}. {item.name:20s}")
        
        # 顯示官方排名
        print("\n【NASA 官方排名】")
        print("-" * 80)
        for item in self.OFFICIAL_ITEMS:
            print(f"{item.official_rank:2d}. {item.name:20s}")
        
        # 計算準確度
        print("\n" + "=" * 80)
        print("準確度分析")
        print("=" * 80)
        
        team_score = self.calculate_accuracy(self.team_ranking)
        
        print(f"\n團隊總分: {team_score}")
        print(f"最佳可能分數: 0")
        print(f"最差可能分數: {sum(range(len(self.items)))}")
        
        # 個人準確度
        print("\n【個人準確度】")
        print("-" * 80)
        for person_name, ranking in self.individual_rankings.items():
            score = self.calculate_accuracy(ranking)
            print(f"{person_name:20s}: {score:4d} 分")
    
    def calculate_accuracy(self, ranking: List[Item]) -> int:
        """計算與官方排名的差異（絕對誤差總和）"""
        score = 0
        for i, item in enumerate(ranking):
            official_rank = item.official_rank - 1
            team_rank = i
            score += abs(official_rank - team_rank)
        return score
    
    def run_single_mode(self) -> None:
        """單人模式"""
        self.display_items()
        self.get_individual_ranking("玩家")
        self.calculate_team_ranking()
        
        # 顯示玩家排名 vs 官方排名
        print("\n" + "=" * 80)
        print("結果")
        print("=" * 80)
        
        player_ranking = self.individual_rankings["玩家"]
        score = self.calculate_accuracy(player_ranking)
        
        print("\n【你的排名】")
        for rank, item in enumerate(player_ranking, 1):
            official = item.official_rank
            diff = rank - official
            symbol = "✓" if diff == 0 else "✗"
            print(f"{symbol} {rank:2d}. {item.name:20s} (官方排名: {official:2d})")
        
        print(f"\n準確度分數: {score}")
        print(f"分數越低越好 (最佳: 0)")
    
    def run_team_mode(self) -> None:
        """團隊模式"""
        self.display_items()
        
        num_people = int(input("有多少人參與？ "))
        for i in range(num_people):
            person_name = input(f"第 {i+1} 個人的名字: ")
            self.get_individual_ranking(person_name)
        
        self.calculate_team_ranking()
        self.display_results()


def main():
    """主程式"""
    print("🌙 月球倖存實驗 🌙\n")
    print("選擇遊戲模式:")
    print("1. 單人模式")
    print("2. 團隊模式\n")
    
    choice = input("請選擇 (1 或 2): ").strip()
    
    experiment = MoonSurvivalExperiment()
    
    if choice == "1":
        experiment.run_single_mode()
    elif choice == "2":
        experiment.run_team_mode()
    else:
        print("❌ 無效選擇")


if __name__ == "__main__":
    main()
