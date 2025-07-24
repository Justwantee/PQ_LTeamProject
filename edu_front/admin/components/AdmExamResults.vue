<template>
    <div>
        <el-row>
            <el-col :span="24">
                <el-card>
                    <div slot="header">
                        <span>考试成绩总览</span>
                        <el-button style="float: right; padding: 3px 0" type="text" @click="refreshData">刷新数据</el-button>
                    </div>

                    <!-- 过滤和搜索区域 -->
                    <el-row :gutter="20" style="margin-bottom: 20px;">
                        <el-col :span="6">
                            <el-input 
                                placeholder="搜索课程名称" 
                                v-model="searchCourse" 
                                clearable>
                            </el-input>
                        </el-col>
                        <el-col :span="6">
                            <el-input 
                                placeholder="搜索考试名称" 
                                v-model="searchExam" 
                                clearable>
                            </el-input>
                        </el-col>
                        <el-col :span="6">
                            <el-input 
                                placeholder="搜索学生ID/姓名" 
                                v-model="searchStudent" 
                                clearable>
                            </el-input>
                        </el-col>
                        <el-col :span="6">
                            <el-button type="primary" @click="applyFilters">应用过滤</el-button>
                            <el-button @click="resetFilters">重置</el-button>
                        </el-col>
                    </el-row>

                    <!-- 统计信息卡片 -->
                    <el-row :gutter="20" style="margin-bottom: 20px;">
                        <el-col :span="6">
                            <el-card shadow="hover">
                                <div style="text-align: center">
                                    <h3>考试总数</h3>
                                    <p style="font-size: 24px; color: #409EFF">{{ stats.totalExams }}</p>
                                </div>
                            </el-card>
                        </el-col>
                        <el-col :span="6">
                            <el-card shadow="hover">
                                <div style="text-align: center">
                                    <h3>参与考试学生</h3>
                                    <p style="font-size: 24px; color: #67C23A">{{ stats.totalStudents }}</p>
                                </div>
                            </el-card>
                        </el-col>
                        <el-col :span="6">
                            <el-card shadow="hover">
                                <div style="text-align: center">
                                    <h3>未评分试卷</h3>
                                    <p style="font-size: 24px; color: #E6A23C">{{ stats.ungraded }}</p>
                                </div>
                            </el-card>
                        </el-col>
                        <el-col :span="6">
                            <el-card shadow="hover">
                                <div style="text-align: center">
                                    <h3>平均分</h3>
                                    <p style="font-size: 24px; color: #F56C6C">{{ stats.averageScore }}</p>
                                </div>
                            </el-card>
                        </el-col>
                    </el-row>

                    <!-- 表格数据 -->
                    <el-table
                        v-loading="loading"
                        :data="filteredExamData"
                        style="width: 100%"
                        border
                        :row-class-name="tableRowClassName"
                        @row-click="handleRowClick">
                        <el-table-column prop="courseName" label="课程名称" min-width="150"></el-table-column>
                        <el-table-column prop="examName" label="考试名称" min-width="150"></el-table-column>
                        <el-table-column prop="studentCount" label="参与学生" width="100"></el-table-column>
                        <el-table-column prop="avgScore" label="平均分" width="100"></el-table-column>
                        <el-table-column prop="maxScore" label="最高分" width="100"></el-table-column>
                        <el-table-column prop="minScore" label="最低分" width="100"></el-table-column>
                        <el-table-column prop="passRate" label="及格率" width="100">
                            <template slot-scope="scope">
                                {{ scope.row.passRate }}%
                            </template>
                        </el-table-column>
                        <el-table-column label="评分状态" width="120">
                            <template slot-scope="scope">
                                <el-tag :type="scope.row.gradedStatus === '已全部评分' ? 'success' : 'warning'">
                                    {{ scope.row.gradedStatus }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" width="200">
                            <template slot-scope="scope">
                                <el-button size="mini" type="primary" @click.stop="viewExamDetails(scope.row)">查看详情</el-button>
                                <el-button size="mini" type="success" @click.stop="exportResults(scope.row)">导出成绩</el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <!-- 分页器 -->
                    <div style="text-align: center; margin-top: 20px">
                        <el-pagination
                            @size-change="handleSizeChange"
                            @current-change="handleCurrentChange"
                            :current-page="currentPage"
                            :page-sizes="[10, 20, 30, 50]"
                            :page-size="pageSize"
                            layout="total, sizes, prev, pager, next, jumper"
                            :total="totalItems">
                        </el-pagination>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 学生成绩详情对话框 -->
        <el-dialog title="学生成绩详情" :visible.sync="dialogVisible" width="80%" center>
            <div v-if="currentExam">
                <h2>{{ currentExam.courseName }} - {{ currentExam.examName }}</h2>

                <el-table
                    :data="studentScores"
                    style="width: 100%"
                    border>
                    <el-table-column prop="username" label="学生姓名" width="120"></el-table-column>
                    <el-table-column prop="userId" label="学号" width="120"></el-table-column>
                    <el-table-column prop="score" label="总分" width="100"></el-table-column>
                    <el-table-column prop="objectiveScore" label="客观题分数" width="120"></el-table-column>
                    <el-table-column prop="subjectiveScore" label="主观题分数" width="120"></el-table-column>
                    <el-table-column label="状态" width="120">
                        <template slot-scope="scope">
                            <el-tag :type="scope.row.isChecked ? 'success' : 'warning'">
                                {{ scope.row.isChecked ? '已评分' : '待评分' }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="交卷时间" min-width="180">
                        <template slot-scope="scope">
                            {{ formatDateTime(scope.row.submitTime) }}
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120">
                        <template slot-scope="scope">
                            <el-button size="mini" type="primary" @click="viewStudentExam(scope.row)">查看试卷</el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
            <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
            </span>
        </el-dialog>
    </div>
</template>

<script>
    export default {
        name: "AdmExamResults",
        data() {
            return {
                loading: false,
                examData: [],         // 所有考试数据
                filteredExamData: [], // 过滤后的数据
                currentPage: 1,
                pageSize: 10,
                totalItems: 0,

                // 搜索过滤
                searchCourse: '',
                searchExam: '',
                searchStudent: '',

                // 统计数据
                stats: {
                    totalExams: 0,
                    totalStudents: 0,
                    ungraded: 0,
                    averageScore: '0.0',
                },

                // 对话框
                dialogVisible: false,
                currentExam: null,
                studentScores: [],
            }
        },
        created() {
            this.fetchAllExams();
        },
        methods: {
            // 获取所有考试数据
            fetchAllExams() {
                this.loading = true;

                // 使用已有的API获取所有考试信息
                // 由于可能没有专用的管理员API，我们先使用模拟数据展示功能
                // 实际实现时应联系后端开发合适的API

                // 告知用户当前使用模拟数据
                this.$notify({
                    title: '提示',
                    message: '当前显示为模拟数据，实际使用时请联系后端开发API',
                    type: 'info',
                    duration: 5000
                });

                // 使用模拟数据演示功能
                this.examData = this.getMockData();
                this.calculateStats();
                this.applyFilters();
                this.loading = false;

                /* 以下是实际API调用的示例，等后端API开发完成后可以取消注释
                this.$axios.get("/Exam/getAllExams").then(res => {
                    if (res.data.flag && res.data.data) {
                        // 处理考试数据，可能需要进一步处理和格式化
                        let exams = res.data.data;
                        // 处理每个考试的详细信息和学生成绩统计
                        this.processExamData(exams);
                    } else {
                        this.$message.error("获取考试数据失败");
                        this.examData = this.getMockData();
                        this.calculateStats();
                        this.applyFilters();
                    }
                    this.loading = false;
                }).catch(err => {
                    console.error(err);
                    this.$message.error("获取考试数据失败");
                    this.examData = this.getMockData();
                    this.calculateStats();
                    this.applyFilters();
                    this.loading = false;
                });
                */
            },

            // 计算统计数据
            calculateStats() {
                // 考试总数
                this.stats.totalExams = this.examData.length;

                // 统计学生总数、未评分数和平均分
                let totalStudents = 0;
                let totalUngraded = 0;
                let scoreSum = 0;
                let scoreCount = 0;

                this.examData.forEach(exam => {
                    totalStudents += exam.studentCount;
                    totalUngraded += exam.ungradedCount || 0;

                    if (exam.avgScore && exam.avgScore > 0) {
                        scoreSum += parseFloat(exam.avgScore) * exam.studentCount;
                        scoreCount += exam.studentCount;
                    }
                });

                this.stats.totalStudents = totalStudents;
                this.stats.ungraded = totalUngraded;
                this.stats.averageScore = scoreCount > 0 ? (scoreSum / scoreCount).toFixed(1) : '0.0';
            },

            // 应用过滤
            applyFilters() {
                let filtered = [...this.examData];

                if (this.searchCourse) {
                    filtered = filtered.filter(item => 
                        item.courseName.toLowerCase().includes(this.searchCourse.toLowerCase())
                    );
                }

                if (this.searchExam) {
                    filtered = filtered.filter(item => 
                        item.examName.toLowerCase().includes(this.searchExam.toLowerCase())
                    );
                }

                // 学生过滤可能需要额外的API调用
                // 这里只做简单的模拟

                // 更新分页数据
                this.totalItems = filtered.length;
                this.filteredExamData = filtered.slice(
                    (this.currentPage - 1) * this.pageSize,
                    this.currentPage * this.pageSize
                );
            },

            // 重置过滤
            resetFilters() {
                this.searchCourse = '';
                this.searchExam = '';
                this.searchStudent = '';
                this.applyFilters();
            },

            // 处理从API获取的考试数据
            processExamData(exams) {
                // 这个方法会在实际API开发完成后使用
                // 将原始考试数据转换为我们需要的格式
                let processedData = [];

                // 对每个考试，需要获取其学生成绩统计信息
                exams.forEach(exam => {
                    // 这里需要调用另一个API来获取考试的详细成绩信息
                    this.$axios.post("/Answer/getAllUserAnswer", {examId: exam.examId}).then(res => {
                        if (res.data.flag && res.data.data) {
                            const studentAnswers = res.data.data;

                            // 计算统计信息
                            let submittedCount = 0;
                            let gradedCount = 0;
                            let totalScore = 0;
                            let maxScore = 0;
                            let minScore = 100;
                            let passCount = 0; // 假设及格分数为60分

                            studentAnswers.forEach(student => {
                                if (student.submit) {
                                    submittedCount++;
                                }

                                if (student.isCheckedBool) {
                                    gradedCount++;
                                    const score = student.score;

                                    totalScore += score;
                                    maxScore = Math.max(maxScore, score);
                                    minScore = Math.min(minScore, score);

                                    if (score >= 60) {
                                        passCount++;
                                    }
                                }
                            });

                            // 创建格式化的数据对象
                            processedData.push({
                                examId: exam.examId,
                                courseId: exam.courseId,
                                courseName: exam.courseName || "未知课程",
                                examName: exam.title || "未命名考试",
                                studentCount: submittedCount,
                                avgScore: submittedCount > 0 ? (totalScore / gradedCount).toFixed(1) : "0.0",
                                maxScore: maxScore.toString(),
                                minScore: minScore === 100 ? "0" : minScore.toString(),
                                passRate: gradedCount > 0 ? Math.round((passCount / gradedCount) * 100) : 0,
                                gradedStatus: gradedCount === submittedCount ? "已全部评分" : "部分未评分",
                                ungradedCount: submittedCount - gradedCount
                            });

                            // 数据处理完成后更新视图
                            if (processedData.length === exams.length) {
                                this.examData = processedData;
                                this.calculateStats();
                                this.applyFilters();
                            }
                        }
                    }).catch(err => {
                        console.error("获取考试答案数据失败:", err);
                    });
                });
            },

            // 刷新数据
            refreshData() {
                this.fetchAllExams();
                this.$message.success("数据已刷新");
            },

            // 分页处理
            handleSizeChange(size) {
                this.pageSize = size;
                this.applyFilters();
            },

            handleCurrentChange(page) {
                this.currentPage = page;
                this.applyFilters();
            },

            // 表格行样式
            tableRowClassName({row, rowIndex}) {
                if (rowIndex % 2 === 0) {
                    return 'row-even';
                } else {
                    return 'row-odd';
                }
            },

            // 行点击
            handleRowClick(row) {
                this.viewExamDetails(row);
            },

            // 查看考试详情
            viewExamDetails(exam) {
                this.currentExam = exam;
                this.dialogVisible = true;
                this.fetchStudentScores(exam.examId);
            },

            // 获取学生成绩
            fetchStudentScores(examId) {
                this.$axios.post("/Answer/getAllUserAnswer", { examId: examId }).then(res => {
                    if (res.data.flag) {
                        this.studentScores = res.data.data;
                    } else {
                        // 如果API不存在，使用模拟数据
                        this.studentScores = this.getMockStudentScores();
                        this.$message.warning("获取学生成绩数据失败，使用模拟数据");
                    }
                }).catch(err => {
                    console.error(err);
                    // 如果API不存在，使用模拟数据
                    this.studentScores = this.getMockStudentScores();
                    this.$message.warning("获取学生成绩数据失败，使用模拟数据");
                });
            },

            // 查看学生试卷
            viewStudentExam(student) {
                if (!this.currentExam) return;

                this.$router.push({
                    name: 'ExamInfoView',
                    params: {
                        examId: this.currentExam.examId,
                        studentId: student.userId
                    }
                });
            },

            // 导出成绩
            exportResults(exam) {
                this.$message.info("正在准备导出数据...");

                // 获取该考试的所有学生成绩
                this.$axios.post("/Answer/getAllUserAnswer", {examId: exam.examId}).then(res => {
                    if (res.data.flag && res.data.data) {
                        const students = res.data.data;

                        // 准备CSV数据
                        let csvContent = "学号,姓名,总分,客观题分数,主观题分数,提交状态,评分状态,提交时间\n";

                        students.forEach(student => {
                            const submitStatus = student.submit ? "已提交" : "未提交";
                            const gradeStatus = student.isCheckedBool ? "已评分" : "未评分";
                            const submitTime = student.submit ? this.formatDateTime(student.submitTime) : "未提交";
                            const subjectiveScore = student.score - student.objectiveScore;

                            csvContent += `${student.userId},${student.username},${student.score},${student.objectiveScore},${subjectiveScore},${submitStatus},${gradeStatus},${submitTime}\n`;
                        });

                        // 创建下载链接
                        const encodedUri = encodeURI("data:text/csv;charset=utf-8," + csvContent);
                        const link = document.createElement("a");
                        link.setAttribute("href", encodedUri);
                        link.setAttribute("download", `${exam.courseName}_${exam.examName}_成绩表.csv`);
                        document.body.appendChild(link);

                        // 触发下载
                        link.click();
                        document.body.removeChild(link);

                        this.$message.success("成绩导出成功！");
                    } else {
                        this.$message.error("导出失败：无法获取学生数据");
                    }
                }).catch(err => {
                    console.error("导出失败:", err);
                    this.$message.error("导出失败：系统错误");
                });
            },

            // 格式化日期时间
            formatDateTime(dateTime) {
                if (!dateTime) return '未提交';

                const date = new Date(dateTime);
                return `${date.getFullYear()}-${this.padZero(date.getMonth() + 1)}-${this.padZero(date.getDate())} ${this.padZero(date.getHours())}:${this.padZero(date.getMinutes())}`;
            },

            padZero(num) {
                return num < 10 ? `0${num}` : num;
            },

            // 模拟数据 - 后端API完成后可移除
            getMockData() {
                return [
                    {
                        examId: 1,
                        courseId: 1,
                        courseName: "计算机组成原理",
                        examName: "期中测试",
                        studentCount: 45,
                        avgScore: "76.5",
                        maxScore: "95",
                        minScore: "45",
                        passRate: 85,
                        gradedStatus: "已全部评分",
                        ungradedCount: 0
                    },
                    {
                        examId: 2,
                        courseId: 2,
                        courseName: "数据结构",
                        examName: "期末考试",
                        studentCount: 38,
                        avgScore: "72.3",
                        maxScore: "98",
                        minScore: "40",
                        passRate: 78,
                        gradedStatus: "已全部评分",
                        ungradedCount: 0
                    },
                    {
                        examId: 3,
                        courseId: 3,
                        courseName: "操作系统",
                        examName: "期中测验",
                        studentCount: 42,
                        avgScore: "68.7",
                        maxScore: "92",
                        minScore: "35",
                        passRate: 62,
                        gradedStatus: "待评分(5)",
                        ungradedCount: 5
                    }
                ];
            },

            // 模拟学生成绩数据
            getMockStudentScores() {
                return [
                    {
                        userId: "stu001",
                        username: "张三",
                        score: 85,
                        objectiveScore: 45,
                        subjectiveScore: 40,
                        isChecked: true,
                        submitTime: "2025-07-15 14:30:45"
                    },
                    {
                        userId: "stu002",
                        username: "李四",
                        score: 72,
                        objectiveScore: 38,
                        subjectiveScore: 34,
                        isChecked: true,
                        submitTime: "2025-07-15 13:25:10"
                    },
                    {
                        userId: "stu003",
                        username: "王五",
                        score: 95,
                        objectiveScore: 48,
                        subjectiveScore: 47,
                        isChecked: true,
                        submitTime: "2025-07-15 15:05:22"
                    },
                    {
                        userId: "stu004",
                        username: "赵六",
                        score: 0,
                        objectiveScore: 42,
                        subjectiveScore: 0,
                        isChecked: false,
                        submitTime: "2025-07-15 14:58:33"
                    }
                ];
            }
        }
    }
</script>

<style scoped>
    .row-even {
        background-color: #fafafa;
    }

    .row-odd {
        background-color: #ffffff;
    }

    .el-table .cell {
        text-align: center;
    }

    /* 高亮显示行 */
    .el-table__row:hover {
        cursor: pointer;
    }
</style>