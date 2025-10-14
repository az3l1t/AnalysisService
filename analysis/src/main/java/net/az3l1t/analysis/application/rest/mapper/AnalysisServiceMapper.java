package net.az3l1t.analysis.application.rest.mapper;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;
import org.mapstruct.MappingTarget;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface AnalysisServiceMapper {
    AnalysisResult toAnalysisResult(CreateInResultDto createInResultDto);
    @Mapping(target = "id", ignore = true)
    void mergeAnalysisResult(UpdateInResultDto updateInResultDto, @MappingTarget AnalysisResult analysisResult);
}
