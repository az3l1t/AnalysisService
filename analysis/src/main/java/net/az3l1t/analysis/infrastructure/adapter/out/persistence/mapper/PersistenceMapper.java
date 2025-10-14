package net.az3l1t.analysis.infrastructure.adapter.out.persistence.mapper;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.entity.AnalysisResultDocument;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;

@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)
public interface PersistenceMapper {
    AnalysisResultDocument toEntity(AnalysisResult analysisResult);
    AnalysisResult toModel(AnalysisResultDocument analysisResultDocument);
}