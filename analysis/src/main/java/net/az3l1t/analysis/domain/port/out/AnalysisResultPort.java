package net.az3l1t.analysis.domain.port.out;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import org.springframework.data.domain.Page;
import java.util.Optional;

public interface AnalysisResultPort {
    AnalysisResult save(AnalysisResult result);
    Optional<AnalysisResult> findByIdOptional(String id);
    AnalysisResult findById(String id);
    Page<AnalysisResult> findAll(int page, int size);
    void deleteById(String id);
}
