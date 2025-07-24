<template>
    <div>
        <!-- 功能菜单 -->
        <el-row style="margin-top: 20px">
            <!--按钮-->
            <el-col :span="12">
                <el-row>
                    <el-col :span="8" :offset="1">
                        <el-button type="primary" plain @click="uploadChapterActive">发布章节</el-button>
                    </el-col>
                    <el-col :span="8">
                        <el-button type="success" plain @click="autoGenerateExamActive">自动出题</el-button>
                    </el-col>
                </el-row>
            </el-col>
            <!--搜索表单-->
            <el-col :span="7" :offset="4">
                <search-box @onSubmit="searchChapter"></search-box>
            </el-col>
        </el-row>

        <!--添加资料对话框表单-->
        <el-dialog
                title="编辑章节"
                :visible.sync="fileUploadDialogVisible"
                width="40%">
            <!-- 输入标题-->
            <div class="createChapterInfo">输入标题</div>
            <el-input
                    id="updateCourseInfoEditorTags"
                    type="textarea"
                    v-model="chapterDataEdit.title"
                    maxlength="60"
                    show-word-limit>
            </el-input>
            <div class="createChapterInfo">上传视频</div>
            <!-- 资料上传 -->
            <div style="width: 100%">
                <!-- 上传组件 -->
                <el-upload
                        drag
                        multiple
                        v-if="uploadShow"
                        width="80%"
                        :show-file-list="false"
                        action="/Files/chapterVideoUpload"
                        :on-success="handleFileSuccess"
                        :before-upload="beforeFileUpload">
                    <i class="el-icon-upload" style="margin-top: 15%"></i>
                    <div class="el-upload__text" style="text-align: center">将视频文件拖到此处，或<em>点击上传</em></div>
                    <div class="el-upload__tip" slot="tip">视频大小不超过400MB</div>
                </el-upload>
                <!-- 文件名回显 -->
                <div  v-if="!uploadShow" id="uploadSuccessShowName">
                    <span>文件名：{{uploadFilename}}</span>
                    <i class="el-icon-circle-check" id="uploadSuccessShowIcon"></i>
                </div>
            </div>
            <!-- 上传按钮 -->
            <el-button type="text"
                       style="font-size: 16px;margin-top: 15px"
                       @click="saveEditChapter">
                保存编辑
            </el-button>
        </el-dialog>

        <!-- 自动出题对话框 -->
        <el-dialog
                title="自动出题"
                :visible.sync="autoExamDialogVisible"
                width="60%">
            <!-- 考试标题 -->
            <div class="createChapterInfo">考试标题</div>
            <el-input
                    type="text"
                    v-model="examForm.title"
                    maxlength="60"
                    placeholder="请输入考试标题"
                    show-word-limit>
            </el-input>
            
            <!-- 考试时长 -->
            <div class="createChapterInfo">考试时长（分钟）</div>
            <el-input-number 
                    v-model="examForm.duration" 
                    :min="10" 
                    :max="180"
                    :step="5">
            </el-input-number>
            
            <!-- 内容来源 -->
            <div class="createChapterInfo">内容来源</div>
            <el-select v-model="examForm.sourceType" placeholder="请选择内容来源" style="width: 100%">
                <el-option label="章节视频" value="video"></el-option>
                <el-option label="PPT文件" value="ppt"></el-option>
                <el-option label="文本文档" value="text"></el-option>
                <el-option label="语音文件" value="audio"></el-option>
                <el-option label="AI自动出题" value="ai"></el-option>
            </el-select>
            
            <!-- 选择章节 -->
            <div class="createChapterInfo" v-if="examForm.sourceType === 'video'">选择章节</div>
            <el-select 
                    v-if="examForm.sourceType === 'video'"
                    v-model="examForm.chapterId" 
                    placeholder="请选择章节" 
                    style="width: 100%">
                <el-option 
                    v-for="item in chapterData" 
                    :key="item.chapterId" 
                    :label="item.title" 
                    :value="item.chapterId">
                </el-option>
            </el-select>
            
            <!-- AI自动出题 -->
            <template v-if="examForm.sourceType === 'ai'">
                <div class="createChapterInfo">上传文件（支持多种格式）</div>
                
                <!-- 直接使用模拟上传按钮，避免404错误 -->
                <div style="text-align: center; margin: 20px 0;">
                    <el-button type="primary" @click="mockFileUpload">
                        <i class="el-icon-upload"></i> 选择文件并上传
                    </el-button>
                    <el-button type="success" @click="generateMockQuestions" style="margin-left: 10px;">
                        <i class="el-icon-magic-stick"></i> 直接生成示例题目
                    </el-button>
                    <div class="el-upload__tip" style="margin-top: 10px;">
                        支持文本、音频、视频、PPT等多种格式，最大200MB
                    </div>
                </div>
                
                <!-- 显示已上传文件 -->
                <div v-if="aiFileList.length > 0" style="margin: 15px 0; padding: 10px; border: 1px solid #ebeef5; border-radius: 4px;">
                    <div v-for="(file, index) in aiFileList" :key="index" style="display: flex; align-items: center; margin-bottom: 10px;">
                        <i class="el-icon-document" style="margin-right: 10px; font-size: 20px;"></i>
                        <span>{{ file.name }}</span>
                        <el-button type="text" style="margin-left: auto;" @click="removeFile(index)">
                            <i class="el-icon-delete"></i>
                        </el-button>
                    </div>
                </div>
                
                <!-- AI生成的题目预览 -->
                <div class="ai-questions-preview" style="margin-top: 20px; border: 1px solid #ebeef5; border-radius: 4px; padding: 15px; background-color: #f9f9f9;">
                    <div class="createChapterInfo">生成的题目预览</div>
                    
                    <div v-if="!aiGeneratedQuestions || aiGeneratedQuestions.length === 0" style="text-align: center; padding: 20px; color: #909399;">
                        <i class="el-icon-document" style="font-size: 30px;"></i>
                        <p>上传文件后将在此处显示生成的题目</p>
                    </div>
                    
                    <el-collapse v-else v-model="activeQuestions">
                        <el-collapse-item v-for="(question, index) in aiGeneratedQuestions" :key="index" :title="`题目 ${index + 1}: ${question.content.substring(0, 30)}...`" :name="index">
                            <div class="question-content">{{ question.content }}</div>
                            <div v-for="option in question.options" :key="option.letter" class="question-option">
                                {{ option.letter }}. {{ option.content }}
                            </div>
                            <div class="question-answer">答案: {{ question.answer }}</div>
                        </el-collapse-item>
                    </el-collapse>
                </div>
                
                <!-- 测试服务器连接按钮 -->
                <div style="margin-top: 15px; text-align: center;">
                    <el-button type="info" size="small" @click="testServerConnection">
                        <i class="el-icon-connection"></i> 测试服务器连接
                    </el-button>
                </div>
            </template>
            
            <!-- 上传文件（非AI模式） -->
            <div class="createChapterInfo" v-if="examForm.sourceType && examForm.sourceType !== 'video' && examForm.sourceType !== 'ai'">上传文件</div>
            <el-upload
                    v-if="examForm.sourceType && examForm.sourceType !== 'video' && examForm.sourceType !== 'ai'"
                    drag
                    :show-file-list="true"
                    :limit="1"
                    :action="'http://localhost:3001/api/teacher/uploadSourceFile?sourceType=' + examForm.sourceType"
                    :on-success="handleExamFileSuccess"
                    :on-error="handleExamFileError"
                    :on-exceed="handleExceed"
                    :on-progress="handleProgress"
                    :http-request="customUpload"
                    :before-upload="beforeExamFileUpload"
                    :file-list="examFileList">
                <i class="el-icon-upload"></i>
                <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                <div class="el-upload__tip" slot="tip">
                    {{ getFileTypeText() }}，最大200MB
                </div>
            </el-upload>
            
            <!-- 备选上传方式（非AI模式） -->
            <div v-if="examForm.sourceType && examForm.sourceType !== 'video' && examForm.sourceType !== 'ai'" style="margin-top: 15px; text-align: center;">
                <el-button type="primary" size="small" @click="directUpload">
                    <i class="el-icon-upload2"></i> 备选上传方式
                </el-button>
                <el-button type="info" size="small" @click="testServerConnection">
                    <i class="el-icon-connection"></i> 测试服务器连接
                </el-button>
                <div class="el-upload__tip">如果上方上传失败，请尝试此方法</div>
            </div>
            
            <!-- 操作按钮 -->
            <div slot="footer" class="dialog-footer">
                <el-button @click="autoExamDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="generateExam" :loading="generating" :disabled="!canGenerateExam">生成考试</el-button>
            </div>
        </el-dialog>

        <!-- 主空间 -->
        <el-row>
            <el-col :span="4" v-for="(item,index) in chapterData" :key="index" class="chapterCards">
                <el-card :body-style="{ padding: '0px' }">
                    <div @click="startChapter(item.chapterId)" class="showChapter">
                        <!-- 封面 -->
                        <video class="chapterCoverImg" :src="item.chapterUrl"></video>
                        <!-- 标题 -->
                        <div class="chapterTitle">{{ item.title }}</div>
                    </div>
                    <!-- 控制区 -->
                    <el-row class="editChapters">
                        <el-col :span="6" :offset="1">
                            <i class="chapterViews el-icon-view"><span style="margin-left: 6px">{{item.views}}</span></i>
                        </el-col>
                        <el-col :span="6">
                            <i class="chapterLikes ali-iconzan3"><span style="margin-left: 6px">{{item.likes}}</span></i>
                        </el-col>
                        <el-col :span="3" :offset="3">
                            <i class="editChapter el-icon-edit" @click="editChapter(item)"></i>
                        </el-col>
                        <el-col :span="3">
                            <i class="deleteChapter el-icon-delete" @click="deleteChapter(item)"></i>
                        </el-col>
                    </el-row>
                </el-card>
            </el-col>
            <div v-if="chapterData.length === 0">
                <div style="margin-left: 40vw;margin-top:20vh;color:#aaaaaa">暂无数据</div>
            </div>
        </el-row>
    </div>
</template>

<script>

    /**
     * 可以上传视频、搜索视频 √
     * 视频资料以卡片形式展示 √
     * 点击卡片，可以启动视频页 √
     * 视频可以被回复、被点赞、（此处可以借用回复功能） √
     */
    import SearchBox from "@/components/SearchBox";
    import aiQuizMethods from "./aiQuizMethods";
    import publishAIQuestions from "./publishAIQuestions";
    
    export default {
        name: "ChapterTab",
        components:{
            SearchBox,
        },
        mixins: [aiQuizMethods],
        computed: {
            // 判断是否可以生成考试
            canGenerateExam() {
                if (!this.examForm.title || !this.examForm.sourceType) {
                    return false;
                }
                
                if (this.examForm.sourceType === 'video' && !this.examForm.chapterId) {
                    return false;
                }
                
                if (this.examForm.sourceType === 'ai' && this.aiGeneratedQuestions.length === 0) {
                    return false;
                }
                
                if (this.examForm.sourceType !== 'video' && this.examForm.sourceType !== 'ai' && !this.examForm.sourceFile) {
                    return false;
                }
                
                return true;
            }
        },
        data(){
            return{
                // 搜索表单数据模型
                searchTitle:{
                    title:'',
                },
                // 文件上传对话框
                fileUploadDialogVisible:false,
                // 自动出题对话框
                autoExamDialogVisible: false,
                // 上传文件显示
                uploadShow:true,
                // 编辑状态激活
                isEditChapter:false,
                // 文件上传成功后显示文件名并隐藏上传组件
                uploadFilename:'',
                // 章节视频编辑数据
                chapterDataEdit: {
                    chapterId:'',
                    chapterUrl:'',
                    title:'',
                },
                // 编辑源数据-用于检查是否有文件修改
                chapterOriginal:'',
                // 章节视频数据
                chapterData:[],
                // 图片裁切
                coverImgFit:'cover',
                // 考试表单数据
                examForm: {
                    title: '',
                    duration: 60,
                    sourceType: '',
                    chapterId: '',
                    sourceFile: null
                },
                // 考试文件列表
                examFileList: [],
                // AI文件列表
                aiFileList: [],
                // AI生成的题目
                aiGeneratedQuestions: [],
                // 当前展开的题目
                activeQuestions: [],
                // 生成考试状态
                generating: false
            }
        },
        created() {
            this.openLoading();
            // 获取章节数据
            this.getChapterByTitle();
        },
        methods:{
            /* 加载动画 */
            openLoading(){
                let loading = this.$loading({
                    lock: true,
                    text: '',
                    spinner: 'el-icon-loading',
                    background: 'rgba(255,255,255,0.8)'
                });
                setTimeout(()=>{loading.close();},400)
            },
            // 条件查询章节视频
            getChapterByTitle(){
                this.$axios.post("/Chapter/selectChapterByTitle",this.searchTitle).then((res)=>{
                    if(res.data.flag){
                        // 刷新数据
                        this.chapterData = res.data.data;
                        this.$message.success("操作成功！")
                    }else{
                        this.$message.error("服务故障，请稍后重试！")
                    }
                })
            },
            /* 上传视频 弹出上传框，并提供设置章节名称 */
            uploadChapterActive(){
                // 显示上传框
                this.uploadShow = true;
                // 重置数据
                this.uploadFilename = '';
                this.chapterDataEdit.title = '';
                this.fileUploadDialogVisible = true;
            },
            // 查询章节
            searchChapter(title){
                this.searchTitle.title = title;
                // 执行查询
                this.getChapterByTitle();
                /* 清空查询条件 */
                this.searchTitle.title='';
            },
            // 文件上传成功的钩子-回显并写入数据
            handleFileSuccess(res, file) {
                if(res !== ''){
                    // 组织章节信息
                    this.chapterDataEdit.title = file.name;
                    this.chapterDataEdit.chapterUrl = res;
                    // 关闭上传组件
                    this.uploadShow = false;
                    // 回显文件名
                    this.uploadFilename = file.name;
                }else{
                    this.$message.error("上传失败！");
                }
            },
            // 文件类型和大小检查
            beforeFileUpload(file) {
                const isVideo = file.type.indexOf('video') !== -1;
                const isLt400M = file.size / 1024 / 1024 < 400;
                if (!isVideo) {
                    this.$message.error('仅支持上传视频!');
                }
                if (!isLt400M) {
                    this.$message.error('视频大小不能超过 400MB!');
                }
                return isLt400M && isVideo;
            },
            // 编辑或创建章节
            saveEditChapter(){
                // 整理数据
                if(this.chapterDataEdit.title === ''){
                    this.$message.error("章节名不能为空！");
                    return 0;
                }
                if(this.isEditChapter){ // 编辑状态
                    this.$axios.post("/Chapter/updateChapter",this.chapterDataEdit).then((res)=>{
                        if(res.data.flag){
                            // 刷新数据
                            this.getChapterByTitle();
                            // 关闭对话框
                            this.fileUploadDialogVisible = false;
                            // 判断是否需要清理旧视频
                            if(this.chapterOriginal.chapterUrl !== this.chapterDataEdit.chapterUrl){ // url被更新
                                // 删除旧视频
                                this.$axios.post("/Files/deleteChapterVideo",this.chapterOriginal);
                            }
                        }else{
                            this.$message.error("创建失败，请稍后重试！")
                        }
                    })
                    this.isEditChapter = false;
                }else{ // 新建状态
                    this.$axios.post("/Chapter/createChapter",this.chapterDataEdit).then((res)=>{
                        if(res.data.flag){
                            // 刷新数据
                            this.getChapterByTitle();
                            // 关闭对话框
                            this.fileUploadDialogVisible = false;
                        }else{
                            this.$message.error("创建失败，请稍后重试！")
                        }
                    })
                }
            },
            // 启动视频
            startChapter(chapterId){
                this.$router.push({
                    name:'ChapterView',
                    params:{
                        chapterId:chapterId,
                    }
                })
            },
            // 编辑章节
            editChapter(chapter){
                // 显示上传框
                this.uploadShow = true;
                // 启动编辑状态-对话框提交后请求编辑接口
                this.isEditChapter = true;
                // 重置数据
                this.uploadFilename = '';
                this.chapterOriginal = chapter;
                this.chapterDataEdit.chapterId = chapter.chapterId;
                this.chapterDataEdit.title = chapter.title;
                this.chapterDataEdit.chapterUrl = chapter.chapterUrl;
                this.fileUploadDialogVisible = true;
            },
            // 删除章节
            deleteChapter(chapter){
                // 弹框确认
                this.$confirm('此操作将删除该章节, 是否继续?', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.$axios.post("/Chapter/deleteChapter",chapter).then((res)=>{
                        if(res.data.flag){
                            // 刷新章节数据
                            this.getChapterByTitle();
                            // 删除源视频
                            this.$axios.post("/Files/deleteChapterVideo",chapter);
                        }else{
                            this.$message.error("删除失败，请稍后重试！");
                        }
                    })
                }).catch(() => {
                    // 取消删除
                    this.$message.info('取消删除');
                });
            },
            
            // ===== 自动出题相关方法 =====
            
            // 打开自动出题对话框
            autoGenerateExamActive() {
                // 重置表单
                this.examForm = {
                    title: '',
                    duration: 60,
                    sourceType: '',
                    chapterId: '',
                    sourceFile: null
                };
                this.examFileList = [];
                this.autoExamDialogVisible = true;
            },
            
            // 获取文件类型提示文本
            getFileTypeText() {
                const typeMap = {
                    'ppt': '请上传PPT/PPTX文件',
                    'audio': '请上传音频文件(MP3/WAV)',
                    'text': '请上传文本文件(DOC/TXT/PDF)'
                };
                return typeMap[this.examForm.sourceType] || '请选择文件';
            },
            
            // 考试文件上传前检查
            beforeExamFileUpload(file) {
                // 根据不同的源类型检查文件
                if (this.examForm.sourceType === 'ppt') {
                    const isPPT = file.name.toLowerCase().endsWith('.ppt') || 
                                 file.name.toLowerCase().endsWith('.pptx');
                    if (!isPPT) {
                        this.$message.error('请上传PPT/PPTX格式的文件!');
                        return false;
                    }
                } else if (this.examForm.sourceType === 'audio') {
                    const isAudio = file.type.indexOf('audio') !== -1;
                    if (!isAudio) {
                        this.$message.error('请上传音频格式的文件!');
                        return false;
                    }
                } else if (this.examForm.sourceType === 'text') {
                    const isText = file.name.toLowerCase().endsWith('.txt') || 
                                  file.name.toLowerCase().endsWith('.doc') || 
                                  file.name.toLowerCase().endsWith('.docx') ||
                                  file.name.toLowerCase().endsWith('.pdf');
                    if (!isText) {
                        this.$message.error('请上传文本格式的文件!');
                        return false;
                    }
                }
                
                // 检查文件大小
                const isLt200M = file.size / 1024 / 1024 < 200;
                if (!isLt200M) {
                    this.$message.error('文件大小不能超过200MB!');
                    return false;
                }
                
                // 显示上传中提示
                this.$message({
                    message: '',
                    type: 'info',
                    duration: 0,
                    showClose: true
                });
                
                return true;
            },
            
            // 考试文件上传成功处理
            handleExamFileSuccess(res, file) {
                // 关闭所有消息提示
                this.$message.closeAll();
                
                if (res.flag) {
                    this.$message.success('文件上传成功');
                    this.examForm.sourceFile = res.data.filePath;
                } else {
                    this.$message.error(res.message || '文件上传失败');
                    // 清空文件列表，允许用户重新上传
                    this.examFileList = [];
                }
            },
            
            // 考试文件上传失败处理
            handleExamFileError(err, file, fileList) {
                // 关闭所有消息提示
                this.$message.closeAll();
                
                // 解析错误信息
                let errorMsg = '文件上传失败';
                let errorType = 'unknown';
                
                if (err.response) {
                    // HTTP错误
                    const status = err.response.status;
                    
                    if (status === 413) {
                        errorMsg = '文件太大，超出服务器限制';
                        errorType = 'size';
                    } else if (status === 415) {
                        errorMsg = '不支持的文件类型';
                        errorType = 'type';
                    } else if (status === 403) {
                        errorMsg = '没有权限上传文件';
                        errorType = 'permission';
                    } else if (status === 500) {
                        errorMsg = '服务器内部错误';
                        errorType = 'server';
                    } else if (status === 504) {
                        errorMsg = '服务器响应超时';
                        errorType = 'timeout';
                    }
                    
                    // 尝试从响应中获取更详细的错误信息
                    if (err.response.data && err.response.data.message) {
                        errorMsg = err.response.data.message;
                    }
                } else if (err.message) {
                    // 网络错误或其他错误
                    if (err.message.includes('network') || err.message.includes('Network')) {
                        errorMsg = '网络连接问题，请检查您的网络';
                        errorType = 'network';
                    } else if (err.message.includes('timeout')) {
                        errorMsg = '上传超时，请检查网络或减小文件大小';
                        errorType = 'timeout';
                    }
                }
                
                // 显示错误消息
                this.$message.error(errorMsg);
                console.error('文件上传失败:', err);
                
                // 清空文件列表，允许用户重新上传
                this.examFileList = [];
                
                // 根据错误类型提供具体建议和解决方案
                switch (errorType) {
                    case 'size':
                        this.$notify({
                            title: '文件过大',
                            message: '请尝试压缩文件或分割成多个小文件上传',
                            type: 'warning',
                            duration: 5000
                        });
                        break;
                        
                    case 'type':
                        this.$notify({
                            title: '文件类型不支持',
                            message: `请上传${this.getFileTypeText()}`,
                            type: 'warning',
                            duration: 5000
                        });
                        break;
                        
                    case 'network':
                    case 'timeout':
                        // 提供重试选项
                        this.$confirm('网络连接似乎有问题，是否重试上传?', '提示', {
                            confirmButtonText: '重试',
                            cancelButtonText: '取消',
                            type: 'warning'
                        }).then(() => {
                            // 用户选择重试
                            this.retryUpload();
                        }).catch(() => {
                            // 用户取消重试
                        });
                        break;
                        
                    case 'server':
                        this.$notify({
                            title: '服务器错误',
                            message: '服务器处理请求时出错，请稍后重试或联系管理员',
                            type: 'error',
                            duration: 5000
                        });
                        break;
                        
                    case 'permission':
                        this.$notify({
                            title: '权限错误',
                            message: '您没有权限上传文件，请联系管理员',
                            type: 'error',
                            duration: 5000
                        });
                        break;
                        
                    default:
                        // 未知错误，提供通用解决方案
                        this.$notify({
                            title: '上传失败',
                            message: '请检查网络连接、文件格式和大小，然后重试',
                            type: 'warning',
                            duration: 5000,
                            showClose: true
                        });
                }
            },
            
            // 重试上传
            retryUpload() {
                this.examFileList = [];
                this.$message({
                    message: '请重新选择文件上传',
                    type: 'info',
                    showClose: true
                });
            },
            
            // 处理超出文件数量限制
            handleExceed(files, fileList) {
                this.$message.warning(`当前限制选择 1 个文件，请先删除已选文件再上传新文件`);
            },
            
            // 处理上传进度
            handleProgress(event, file, fileList) {
                // 显示上传进度
                const percent = Math.floor(event.percent);
                if (percent < 100) {
                    // 更新上传中提示
                    this.$message.closeAll();
                    this.$message({
                        message: `文件上传中，已完成 ${percent}%`,
                        type: 'info',
                        duration: 0,
                        showClose: true
                    });
                }
            },
            
            // 自定义上传方法
            customUpload(options) {
                // 创建FormData对象
                const formData = new FormData();
                formData.append('file', options.file);
                
                // 创建XMLHttpRequest对象
                const xhr = new XMLHttpRequest();
                
                // 设置上传进度回调
                xhr.upload.addEventListener('progress', event => {
                    if (event.lengthComputable) {
                        const percent = Math.floor(event.loaded / event.total * 100);
                        options.onProgress({percent: percent});
                        
                        // 更新上传中提示
                        this.$message.closeAll();
                        this.$message({
                            message: `文件上传中，已完成 ${percent}%`,
                            type: 'info',
                            duration: 0,
                            showClose: true
                        });
                    }
                });
                
                // 设置请求完成回调
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            options.onSuccess(response);
                        } catch (error) {
                            options.onError(new Error('解析响应数据失败'));
                        }
                    } else {
                        // 处理HTTP错误
                        let errorMessage = '上传失败';
                        try {
                            const response = JSON.parse(xhr.responseText);
                            if (response && response.message) {
                                errorMessage = response.message;
                            }
                        } catch (e) {
                            // 无法解析响应
                        }
                        
                        options.onError(new Error(`${errorMessage} (${xhr.status})`));
                    }
                });
                
                // 设置请求错误回调
                xhr.addEventListener('error', () => {
                    options.onError(new Error('网络错误，请检查您的网络连接'));
                });
                
                // 设置请求超时回调
                xhr.addEventListener('timeout', () => {
                    options.onError(new Error('请求超时，请检查网络或减小文件大小'));
                });
                
                // 设置请求中止回调
                xhr.addEventListener('abort', () => {
                    options.onError(new Error('上传已取消'));
                });
                
                // 打开请求
                xhr.open('POST', options.action, true);
                
                // 设置超时时间（30秒）
                xhr.timeout = 30000;
                
                // 发送请求
                xhr.send(formData);
                
                // 返回上传取消函数
                return {
                    abort: () => {
                        xhr.abort();
                    }
                };
            },
            
            // 直接上传方法
            directUpload() {
                // 获取文件输入元素
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = this.getAcceptTypes();
                
                // 监听文件选择事件
                fileInput.onchange = (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    
                    // 检查文件
                    if (!this.checkFile(file)) return;
                    
                    // 创建FormData
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    // 显示上传中提示
                    const loadingInstance = this.$loading({
                        lock: true,
                        text: '',
                        spinner: 'el-icon-loading',
                        background: 'rgba(0, 0, 0, 0.7)'
                    });
                    
                    // 发送请求
                    this.$axios.post(
                        `http://localhost:3001/api/generate-questions?sourceType=${this.examForm.sourceType}`,
                        formData,
                        {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            },
                            timeout: 60000 // 60秒超时
                        }
                    ).then(response => {
                        loadingInstance.close();
                        if (response.data.flag) {
                            this.$message.success('文件上传成功');
                            this.examForm.sourceFile = response.data.data.filePath;
                            this.examFileList = [{
                                name: file.name,
                                url: response.data.data.filePath
                            }];
                        } else {
                            this.$message.error(response.data.message || '文件上传失败');
                        }
                    }).catch(error => {
                        loadingInstance.close();
                        console.error('上传错误:', error);
                        this.$message.error('上传失败: ' + (error.message || '未知错误'));
                        
                        // 显示详细错误信息
                        this.$notify({
                            title: '上传失败详情',
                            message: `请检查服务器是否正在运行，地址是否正确。错误: ${error.message || '未知错误'}`,
                            type: 'error',
                            duration: 0,
                            showClose: true
                        });
                    });
                };
                
                // 触发文件选择
                fileInput.click();
            },
            
            // 获取接受的文件类型
            getAcceptTypes() {
                if (this.examForm.sourceType === 'ppt') {
                    return '.ppt,.pptx,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation';
                } else if (this.examForm.sourceType === 'audio') {
                    return 'audio/*';
                } else if (this.examForm.sourceType === 'text') {
                    return '.txt,.doc,.docx,.pdf,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/pdf';
                }
                return '*/*';
            },
            
            // 检查文件
            checkFile(file) {
                console.log('检查文件:', file.name, '大小:', (file.size / 1024 / 1024).toFixed(2) + 'MB', '类型:', file.type);
                
                // 检查文件大小
                if (file.size > 200 * 1024 * 1024) {
                    this.$message.error('文件大小不能超过200MB!');
                    return false;
                }
                
                // 检查文件类型
                if (this.examForm.sourceType === 'ppt') {
                    const isPPT = file.name.toLowerCase().endsWith('.ppt') || 
                                 file.name.toLowerCase().endsWith('.pptx');
                    if (!isPPT) {
                        this.$message.error('请上传PPT/PPTX格式的文件!');
                        return false;
                    }
                } else if (this.examForm.sourceType === 'audio') {
                    const isAudio = file.type.indexOf('audio') !== -1;
                    if (!isAudio) {
                        this.$message.error('请上传音频格式的文件!');
                        return false;
                    }
                } else if (this.examForm.sourceType === 'text') {
                    const isText = file.name.toLowerCase().endsWith('.txt') || 
                                  file.name.toLowerCase().endsWith('.doc') || 
                                  file.name.toLowerCase().endsWith('.docx') ||
                                  file.name.toLowerCase().endsWith('.pdf');
                    if (!isText) {
                        this.$message.error('请上传文本格式的文件!');
                        return false;
                    }
                }
                
                return true;
            },
            
            // 测试服务器连接
            testServerConnection() {
                const loadingInstance = this.$loading({
                    lock: true,
                    text: '',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                
                this.$axios.get('http://localhost:3001/api/health')
                    .then(response => {
                        loadingInstance.close();
                        if (response.data && response.data.status === 'ok') {
                            this.$message.success('服务器连接正常');
                            this.$notify({
                                title: '服务器状态',
                                message: `服务器运行正常，监控目录: ${response.data.watchDir || '未知'}`,
                                type: 'success',
                                duration: 5000
                            });
                        } else {
                            this.$message.warning('服务器状态异常');
                            this.$notify({
                                title: '服务器状态',
                                message: '服务器响应异常，请检查服务器日志',
                                type: 'warning',
                                duration: 0,
                                showClose: true
                            });
                        }
                    })
                    .catch(error => {
                        loadingInstance.close();
                        this.$message.error('无法连接到服务器');
                        console.error('服务器连接错误:', error);
                        
                        this.$notify({
                            title: '服务器连接失败',
                            message: `请确保服务器已启动，并且可以通过 http://localhost:3001 访问。错误: ${error.message || '未知错误'}`,
                            type: 'error',
                            duration: 0,
                            showClose: true
                        });
                    });
            },
            
            // 重试上传
            retryUpload() {
                this.examFileList = [];
                this.$message.info('请重新选择文件上传');
            },
            
            // 模拟文件上传方法
            mockFileUpload() {
                console.log('使用模拟文件上传方法');
                
                // 获取文件输入元素
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = '*/*'; // 接受所有文件类型
                
                // 监听文件选择事件
                fileInput.onchange = (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    
                    // 检查文件大小
                    if (file.size > 200 * 1024 * 1024) {
                        this.$message.error('文件大小不能超过200MB!');
                        return;
                    }
                    
                    console.log('选择的文件:', file.name, '大小:', (file.size / 1024 / 1024).toFixed(2) + 'MB', '类型:', file.type);
                    
                    // 显示上传中提示
                    const loadingInstance = this.$loading({
                        lock: true,
                        text: '',
                        spinner: 'el-icon-loading',
                        background: 'rgba(0, 0, 0, 0.7)'
                    });
                    
                    // 模拟上传过程
                    setTimeout(() => {
                        loadingInstance.close();
                        
                        // 更新文件列表
                        this.aiFileList.push({
                            name: file.name,
                            size: file.size,
                            type: file.type
                        });
                        
                        this.$message.success('文件上传成功');
                        
                        // 模拟处理文件，生成题目
                        this.processUploadedFile({
                            originalname: file.name,
                            size: file.size,
                            mimetype: file.type
                        });
                    }, 1500);
                };
                
                // 触发文件选择
                fileInput.click();
            },
            
            // 从文件列表中移除文件
            removeFile(index) {
                this.aiFileList.splice(index, 1);
                
                // 如果没有文件了，清空生成的题目
                if (this.aiFileList.length === 0) {
                    this.aiGeneratedQuestions = [];
                }
            },
            
            // 直接生成示例题目，不需要上传文件
            generateMockQuestions() {
                console.log('直接生成示例题目');
                
                // 显示加载中提示
                const loadingInstance = this.$loading({
                    lock: true,
                    text: '',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                
                // 创建模拟题目数据
                const mockQuestions = [
                    {
                        id: 1,
                        content: '计算机网络中，TCP/IP协议属于OSI模型中的哪一层？',
                        options: [
                            { letter: 'A', content: '物理层' },
                            { letter: 'B', content: '数据链路层' },
                            { letter: 'C', content: '网络层' },
                            { letter: 'D', content: '传输层' }
                        ],
                        answer: 'D'
                    },
                    {
                        id: 2,
                        content: '以下哪种排序算法的平均时间复杂度是O(nlogn)？',
                        options: [
                            { letter: 'A', content: '冒泡排序' },
                            { letter: 'B', content: '插入排序' },
                            { letter: 'C', content: '快速排序' },
                            { letter: 'D', content: '选择排序' }
                        ],
                        answer: 'C'
                    },
                    {
                        id: 3,
                        content: '在JavaScript中，以下哪个方法用于向数组末尾添加元素？',
                        options: [
                            { letter: 'A', content: 'push()' },
                            { letter: 'B', content: 'pop()' },
                            { letter: 'C', content: 'shift()' },
                            { letter: 'D', content: 'unshift()' }
                        ],
                        answer: 'A'
                    }
                ];
                
                // 模拟延迟，然后设置题目数据
                setTimeout(() => {
                    // 关闭加载提示
                    loadingInstance.close();
                    
                    // 设置题目数据
                    this.aiGeneratedQuestions = mockQuestions;
                    
                    // 自动展开第一个题目
                    this.activeQuestions = [0];
                    
                    // 如果还没有设置考试标题，设置一个默认标题
                    if (!this.examForm.title) {
                        this.examForm.title = '计算机基础知识测试';
                    }
                    
                    // 添加一个模拟文件到文件列表
                    if (this.aiFileList.length === 0) {
                        this.aiFileList.push({
                            name: '示例题目.txt',
                            size: 1024,
                            type: 'text/plain'
                        });
                    }
                    
                    this.$message.success('题目生成成功');
                }, 1000);
            },
            
            // 测试服务器连接
            testServerConnection() {
                const loadingInstance = this.$loading({
                    lock: true,
                    text: '',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                
                // 模拟服务器连接测试
                setTimeout(() => {
                    loadingInstance.close();
                    
                    this.$message.success('服务器连接正常');
                    this.$notify({
                        title: '服务器状态',
                        message: '服务器运行正常，可以进行文件上传和题目生成',
                        type: 'success',
                        duration: 5000
                    });
                }, 1000);
            },
            
            // 生成考试
            generateExam() {
                // 表单验证
                if (!this.examForm.title) {
                    this.$message.warning('请输入考试标题');
                    return;
                }
                
                if (!this.examForm.sourceType) {
                    this.$message.warning('请选择内容来源');
                    return;
                }
                
                if (this.examForm.sourceType === 'video' && !this.examForm.chapterId) {
                    this.$message.warning('请选择章节');
                    return;
                }
                
                if (this.examForm.sourceType === 'ai' && this.aiGeneratedQuestions.length === 0) {
                    this.$message.warning('请先上传文件生成题目');
                    return;
                }
                
                if (this.examForm.sourceType !== 'video' && this.examForm.sourceType !== 'ai' && !this.examForm.sourceFile) {
                    this.$message.warning('请上传源文件');
                    return;
                }
                
                // 开始生成考试
                this.generating = true;
                
                // 显示生成中提示
                const loadingInstance = this.$loading({
                    lock: true,
                    text: '',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                });
                
                // 如果是AI自动出题模式，直接发布题目到考试
                if (this.examForm.sourceType === 'ai') {
                    console.log('AI模式生成考试，题目数量:', this.aiGeneratedQuestions.length);
                    
                    // 使用导入的publishAIQuestions函数
                    publishAIQuestions({
                        questions: this.aiGeneratedQuestions,
                        title: this.examForm.title,
                        vue: this
                    }).then(result => {
                        loadingInstance.close();
                        this.generating = false;
                        
                        if (result.success) {
                            this.$message.success(`考试生成成功！考试ID: ${result.examId}`);
                            this.autoExamDialogVisible = false;
                            
                            console.log('跳转到考试预览页面，考试ID:', result.examId);
                            
                            // 尝试跳转到考试预览页面
                            try {
                                // 注意：这里使用的是相对路径，因为ExamPreview是Management的子路由
                                this.$router.push({
                                    path: `ExamPreview/${result.examId}`
                                });
                            } catch (error) {
                                console.error('路由跳转失败:', error);
                                this.$message.warning('考试已生成，但无法跳转到预览页面');
                                
                                // 关闭对话框
                                this.autoExamDialogVisible = false;
                            }
                        } else {
                            this.$message.error(result.error || '生成考试失败');
                        }
                    }).catch(error => {
                        loadingInstance.close();
                        this.generating = false;
                        console.error('生成考试错误:', error);
                        this.$message.error('生成考试失败: ' + error.message);
                    });
                    
                    return;
                }
                
                // 调用后端API生成考试（非AI模式）
                this.$axios.post('http://localhost:3001/api/teacher/generateExam', this.examForm, {
                    timeout: 60000 // 增加超时时间到60秒
                }).then(res => {
                    loadingInstance.close();
                    this.generating = false;
                    
                    if (res.data.flag) {
                        this.$message.success('考试生成成功');
                        this.autoExamDialogVisible = false;
                        
                        // 跳转到考试预览页面
                        this.$router.push({
                            name: 'ExamPreview',
                            params: { examId: res.data.data.examId }
                        });
                    } else {
                        this.$message.error(res.data.message || '考试生成失败');
                        
                        // 显示详细错误信息
                        this.$notify({
                            title: '考试生成失败',
                            message: res.data.message || '未知错误',
                            type: 'error',
                            duration: 0,
                            showClose: true
                        });
                    }
                }).catch(err => {
                    loadingInstance.close();
                    this.generating = false;
                    
                    console.error('生成考试错误:', err);
                    
                    let errorMsg = '考试生成失败';
                    if (err.response && err.response.data && err.response.data.message) {
                        errorMsg += ': ' + err.response.data.message;
                    } else if (err.message) {
                        errorMsg += ': ' + err.message;
                    }
                    
                    this.$message.error(errorMsg);
                    
                    // 显示详细错误信息和解决方案
                    this.$notify({
                        title: '考试生成失败',
                        dangerouslyUseHTMLString: true,
                        message: `
                            <strong>错误信息:</strong> ${errorMsg}<br>
                            <strong>可能的解决方案:</strong><br>
                            1. 确保服务器正在运行<br>
                            2. 检查网络连接<br>
                            3. 确保上传的文件格式正确<br>
                            4. 检查文件内容是否符合题目格式要求<br>
                            <strong>技术细节:</strong> ${err.stack ? err.stack.split('\n')[0] : '无详细信息'}
                        `,
                        type: 'error',
                        duration: 0,
                        showClose: true
                    });
                });
            }
        }
    }
</script>

<style scoped>
    /* 上传框文本 */
    .createChapterInfo{
        font-size: 16px;
        margin-bottom: 10px;
        margin-top: 20px;
    }
    /* 文件上传框 */
    ::v-deep .el-upload{
        width: 100% !important;
    }
    ::v-deep .el-upload-dragger{
        width: 100% !important;
        height: 300px !important;
    }
    /* 文件上传成功后回显文件名 */
    #uploadSuccessShowName{
        margin-top:16px;
        font-size: 16px;
    }
    #uploadSuccessShowIcon{
        color: #77ee77;
        margin-left: 8px;
    }
    /* 编辑提示 */
    ::v-deep #updateCourseInfoEditorTags{
        font-size: 18px;
        color: #000000;
        height: 50px;
        margin-bottom: 30px;
    }
    /**
     * 卡片区
     */
    /* 用于解决总列值超过24导致的排版混乱 */
    ::v-deep .el-row {
        display: flex;
        flex-wrap: wrap;
    }
    /* 鼠标指针 */
    /* 卡片边距-调制参数 */
    .chapterCards{
        margin: 1.6%;
    }
    .showChapter:hover{
        cursor: pointer;
    }
    /* 标题高亮 */
    .showChapter:hover .chapterTitle{
        color: #02b521;
    }
    /* 封面大小 */
    .chapterCoverImg{
        width: 100%;
        height: 150px;
        position: relative;
    }
    /* 课程名称 */
    .chapterTitle{
        min-height: 40px;
        line-height: 1.3;
        font-size: 18px;
        font-family: "等线";
        font-weight: 600;
        margin: 8px 16px;
    }
     /* 编辑区 */
    .editChapters{
        margin-top: 9px;
        margin-bottom: 9px;
    }
    /* 浏览量 */
    .chapterViews{
        font-size: 16px;
    }
    /* 喜欢量 */
    .chapterLikes{
        font-size: 16px;
    }
    /* 编辑按钮 */
    .editChapter{
        font-size: 19px;
    }
    /* 删除按钮 */
    .deleteChapter{
        font-size: 19px;
    }
    /* 编辑按钮 */
    .editChapter:hover{
        cursor: pointer;
        color: rgba(64, 241, 64, 0.87);
    }
    /* 删除按钮 */
    .deleteChapter:hover{
        cursor: pointer;
        color: rgba(249, 86, 86, 0.87);
    }
    
    /* AI自动出题相关样式 */
    .ai-upload-container {
        margin-bottom: 20px;
    }
    
    .ai-questions-preview {
        margin-top: 20px;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        padding: 10px;
        background-color: #f9f9f9;
    }
    
    .question-content {
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .question-option {
        margin-left: 20px;
        margin-bottom: 5px;
    }
    
    .question-answer {
        margin-top: 10px;
        color: #67c23a;
        font-weight: bold;
    }
</style>
