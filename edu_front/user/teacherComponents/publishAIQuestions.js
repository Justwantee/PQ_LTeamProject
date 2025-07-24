// 单独的发布AI题目到考试的函数
import axios from 'axios';

/**
 * 发布AI生成的题目到考试
 * @param {Object} options - 配置选项
 * @param {Array} options.questions - 题目数组
 * @param {string} options.title - 考试标题
 * @param {Object} options.vue - Vue实例，用于访问$message和$loading
 * @returns {Promise} - 返回Promise对象
 */
export default function publishAIQuestions(options) {
    const { questions, title, vue } = options;
    
    if (!questions || !Array.isArray(questions) || questions.length === 0) {
        vue.$message.warning('没有可发布的题目');
        return Promise.resolve({ success: false, error: '没有可发布的题目' });
    }
    
    // 显示处理中提示
    const loadingInstance = vue.$loading({
        lock: true,
        text: '',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
    });
    
    console.log('准备发布题目到考试，题目数量:', questions.length);
    
    // 调用简化版的考试生成API
    return axios.post('/api/simple-generate-exam', {
        title: title || `AI生成考试 - ${new Date().toISOString().slice(0, 10)}`,
        questions: questions
    })
    .then(response => {
        loadingInstance.close();
        
        if (response.data.success && response.data.examId) {
            vue.$message.success(`题目已成功发布到考试！考试ID: ${response.data.examId}`);
            return {
                success: true,
                examId: response.data.examId
            };
        } else {
            throw new Error(response.data.error || '发布题目失败');
        }
    })
    .catch(error => {
        loadingInstance.close();
        console.error('发布题目出错:', error);
        vue.$message.error(`发布题目失败: ${error.message || '未知错误'}`);
        return {
            success: false,
            error: error.message || '未知错误'
        };
    });
}