package com.diy.sys.controller.Question;

import com.diy.common.vo.Result;
import com.diy.sys.entity.Question.QuestionSet;
import com.diy.sys.service.Question.IQuestionSetService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * <p>
 * 题库控制器
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Tag(name = "题库管理接口")
@RestController
@RequestMapping("/question-set")
public class QuestionSetController {

    @Autowired
    private IQuestionSetService questionSetService;

    /**
     * 新增题库
     * 
     * @param questionSet 题库信息
     * @return 操作结果
     */
    @Operation(summary = "新增题库")
    @PostMapping
    public Result<QuestionSet> addQuestionSet(@RequestBody QuestionSet questionSet) {
        try {
            // 设置默认状态为启用（如果未设置）
            if (questionSet.getStatus() == 0) {
                questionSet.setStatus(1);
            }
            
            boolean success = questionSetService.save(questionSet);
            if (success) {
                return Result.success(questionSet, "新增题库成功");
            } else {
                return Result.fail("新增题库失败");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("新增题库失败：" + e.getMessage());
        }
    }

    /**
     * 修改题库
     * 
     * @param questionSet 题库信息
     * @return 操作结果
     */
    @Operation(summary = "修改题库")
    @PutMapping
    public Result<?> updateQuestionSet(@RequestBody QuestionSet questionSet) {
        try {
            boolean success = questionSetService.updateById(questionSet);
            if (success) {
                return Result.success(questionSet, "修改题库成功");
            } else {
                return Result.fail("修改题库失败");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("修改题库失败：" + e.getMessage());
        }
    }

    /**
     * 分页查询题库列表
     * 
     * @param name 题库名称（模糊查询，可选）
     * @param status 状态（可选）
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    @Operation(summary = "分页查询题库列表")
    @GetMapping("/list")
    public Result<Map<String, Object>> getQuestionSetList(
            @RequestParam(value = "name", required = false) String name,
            @RequestParam(value = "status", required = false) Integer status,
            @RequestParam("pageNo") Long pageNo,
            @RequestParam("pageSize") Long pageSize) {
        try {
            Map<String, Object> data = questionSetService.getQuestionSetList(name, status, pageNo, pageSize);
            return Result.success(data, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID查询单个题库
     * 
     * @param id 题库ID
     * @return 题库信息
     */
    @Operation(summary = "根据ID查询题库")
    @GetMapping("/{id}")
    public Result<QuestionSet> getQuestionSetById(@PathVariable("id") Integer id) {
        try {
            QuestionSet questionSet = questionSetService.getById(id);
            if (questionSet != null) {
                return Result.success(questionSet, "查询成功");
            } else {
                return Result.fail("题库不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID删除题库
     * 
     * @param id 题库ID
     * @return 操作结果
     */
    @Operation(summary = "删除题库")
    @DeleteMapping("/{id}")
    public Result<?> deleteQuestionSetById(@PathVariable("id") Integer id) {
        try {
            boolean success = questionSetService.removeById(id);
            if (success) {
                return Result.success("删除题库成功");
            } else {
                return Result.fail("删除题库失败，题库可能不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("删除题库失败：" + e.getMessage());
        }
    }

    /**
     * 查询所有题库（不分页，用于下拉选择）
     * 
     * @return 题库列表
     */
    @Operation(summary = "查询所有题库")
    @GetMapping("/all")
    public Result<?> getAllQuestionSets() {
        try {
            return Result.success(questionSetService.list(), "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 根据题库ID获取题目ID列表
     * 
     * @param id 题库ID
     * @return 题目ID列表
     */
    @Operation(summary = "获取题库下的题目ID列表")
    @GetMapping("/{id}/questions")
    public Result<List<Integer>> getQuestionIdsByQuestionSetId(@PathVariable("id") Integer id) {
        try {
            List<Integer> questionIds = questionSetService.getQuestionIdsByQuestionSetId(id);
            return Result.success(questionIds, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 更新题库的题目关联
     * 
     * @param id 题库ID
     * @param questionIdList 题目ID列表
     * @return 操作结果
     */
    @Operation(summary = "更新题库的题目关联")
    @PutMapping("/{id}/questions")
    public Result<?> updateQuestionSetQuestions(
            @PathVariable("id") Integer id,
            @RequestBody List<Integer> questionIdList) {
        try {
            questionSetService.updateQuestionSetQuestions(id, questionIdList);
            return Result.success("更新题目关联成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("更新题目关联失败：" + e.getMessage());
        }
    }
}

