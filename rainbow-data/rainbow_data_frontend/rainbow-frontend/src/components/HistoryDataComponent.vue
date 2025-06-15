            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="text" size="small" @click="viewDetail(scope.row)">
                  详情
                </el-button>
                <el-button type="text" size="small" @click="addToFavorites(scope.row)" style="color: #f56c6c;">
                  <el-icon><Star /></el-icon>
                  收藏
                </el-button>
              </template>
            </el-table-column> 